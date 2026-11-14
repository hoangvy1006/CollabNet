"""Client core: network logic + application protocol. No UI code here (see gateway.py / web/).
lớp ClientCore giữ kết nối tới server, tự kết nối lại khi mất mạng, lưu lịch sử tin nhắn/tệp trong
bộ nhớ và phát sự kiện (emit) cho UI. Nhận file ghi vào `*.part` rồi đổi tên sau khi kiểm tra SHA-256.
"""
import asyncio
import hashlib
import json
import logging
import os
import socket
import time
import uuid

from common import crypto
from common.fsutil import atomic_write_json
from common.protocol import MsgBuffer, ProtocolError, pack, safe_filename
from common.transport import Endpoint

log = logging.getLogger("collabnet.client")


class AuthError(Exception):
    """Đăng nhập không hoàn tất (server từ chối, hoặc kết nối đứt giữa chừng khi xác thực)."""


class AuthRejected(AuthError):
    """Server trả AUTH_FAIL: thông tin đăng nhập bị từ chối hẳn. Thử lại tự động sẽ vô ích."""


class ClientCore:
    """Toàn bộ logic mạng phía client. UI (gateway) chỉ đọc trạng thái và nhận sự kiện qua `subscribe()`."""

    def __init__(self, loop, state_dir="./client_state", cc="cubic", sim_loss=0.0, sim_delay=0.0):
        self.loop, self.cc, self.sim_loss, self.sim_delay = loop, cc, sim_loss, sim_delay
        self.state_dir = state_dir
        self.download_dir = os.path.join(state_dir, "downloads")
        os.makedirs(self.download_dir, exist_ok=True)
        self.known_hosts = os.path.join(state_dir, "known_hosts.json")
        self.ep = self.conn = None
        self.user = None
        self.creds = None
        self.peers, self.history, self.files = [], [], []
        self._midx: dict[str, dict] = {}        # message id -> history item (delivery status)
        self._fidx: dict[str, dict] = {}        # file id -> file item (progress / status)
        self.max_file = None                    # server's file-size limit (bytes), learnt at login
        self.subscribers: set[asyncio.Queue] = set()
        self.rx: dict[int, dict] = {}
        self.aborted: set[str] = set()
        self._auth_fut = None
        self._ctrl = MsgBuffer()
        self._want_online = False
        self._stats_on = False
        self._reconnect_task = self._stats_task = None
        self.status = "offline"

    # ------------------------------------------------------------ events
    def subscribe(self):
        q = asyncio.Queue(maxsize=2000)
        self.subscribers.add(q)
        return q

    def unsubscribe(self, q):
        self.subscribers.discard(q)

    def emit(self, typ, **data):
        for q in list(self.subscribers):
            try:
                q.put_nowait((typ, data))
            except asyncio.QueueFull:
                pass

    def snapshot(self):
        # Ảnh chụp để UI dựng lại toàn bộ màn hình sau khi tải lại trang; chỉ gửi phần đuôi lịch sử để
        # payload không tăng vô hạn theo thời gian sử dụng.
        return {"status": self.status, "user": self.user, "peers": self.peers, "history": self.history[-300:],
                "files": self.files[-100:], "stats": self.conn.stats() if self.conn else None, "cc": self.cc,
                "max_file": self.max_file}

    def _remember(self, item, index, store):
        """Keep bounded in-memory history (messages / file transfers) so the UI can rebuild after a reload."""
        store.append(item)
        index[item["id"]] = item
        if len(store) > 2000:
            old = store.pop(0)
            index.pop(old["id"], None)

    # ------------------------------------------------------------ connection management
    def _verify_server(self, host, port):
        # TOFU (trust on first use): lần đầu ghi nhớ fingerprint khoá server; lần sau khác -> từ chối (chống MITM).
        def check(pub: bytes):
            fp, key = crypto.fingerprint(pub), f"{host}:{port}"
            known = {}
            if os.path.exists(self.known_hosts):
                with open(self.known_hosts, encoding="utf-8") as fh:
                    known = json.load(fh)
            if key not in known:                                  # trust on first use (TOFU)
                known[key] = fp
                atomic_write_json(self.known_hosts, known)        # ghi nguyên tử: không hỏng file pin khi crash
                self.emit("notice", level="info", text=f"New server pinned: {fp}")
            elif known[key] != fp:
                raise ConnectionError(f"SERVER KEY CHANGED for {key} (possible man-in-the-middle). "
                                      f"Expected {known[key]}, got {fp}")
        return check

    async def login(self, host, port, user, password):
        await self._disconnect(announce=False)
        self.creds = (host, int(port), user, password)
        await self._connect()
        self._want_online = True

    async def _connect(self):
        host, port, user, password = self.creds
        self.status = "connecting"
        self.emit("status", status=self.status)
        infos = await self.loop.getaddrinfo(host, port, family=socket.AF_INET, type=socket.SOCK_DGRAM)
        addr = infos[0][4]
        ep = Endpoint(self.loop, ("0.0.0.0", 0), cc=self.cc, sim_loss=self.sim_loss, sim_delay=self.sim_delay)
        try:
            conn = await ep.connect(addr, verify=self._verify_server(host, port))
        except BaseException:                                     # kể cả CancelledError: không để rò socket
            ep.close()
            self.status = "offline"
            self.emit("status", status=self.status)
            raise
        self.ep, self.conn = ep, conn
        conn.on_stream_data = self._on_data
        conn.on_close = self._on_conn_close
        self._ctrl, self.rx = MsgBuffer(), {}
        self._auth_fut = self.loop.create_future()
        sid = conn.open_stream(0)
        conn.send(sid, pack({"t": "AUTH", "user": user, "pass": password}))
        try:
            res = await asyncio.wait_for(self._auth_fut, 8)
        except BaseException:
            # Chỉ dọn kết nối của lần _connect này và KHÔNG tắt `_want_online`: lỗi xác thực tạm thời
            # (timeout, rớt mạng giữa chừng) không được làm vòng tự kết nối lại dừng hẳn.
            await self._abandon(ep, conn)
            raise
        self.user, self.peers, self.status = res["user"], res["peers"], "online"
        self.max_file = res.get("max_file")
        self.emit("status", status=self.status, user=self.user)
        self.emit("peers", peers=self.peers)
        self._stats_on = True
        if self._stats_task is None or self._stats_task.done():
            self._stats_task = asyncio.ensure_future(self._stats_loop())

    def _abort_downloads(self):
        for st in self.rx.values():
            fh = st.get("fh")
            if fh and not fh.closed:
                fh.close()
            part = st.get("path")
            if part:
                try:
                    os.remove(part + ".part")
                except OSError:
                    pass
        self.rx.clear()

    async def _abandon(self, ep, conn):
        """Huỷ kết nối dở dang của một lần `_connect` mà không ảnh hưởng tới kết nối của lần khác."""
        if self.conn is conn:
            await self._teardown(announce=False)
        else:
            conn.close(0, "abandoned")
            ep.close()

    async def _disconnect(self, announce=True):
        """Ngắt chủ động (logout / đăng nhập lại): tắt luôn cơ chế tự kết nối lại và huỷ tác vụ đang chờ."""
        self._want_online = False
        task = self._reconnect_task
        if task is not None and not task.done() and task is not asyncio.current_task():
            task.cancel()                      # tránh một _connect cũ chạy song song với đăng nhập mới
        await self._teardown(announce)

    async def _teardown(self, announce=True):
        """Đóng kết nối + endpoint hiện tại, dọn trạng thái; giữ nguyên `_want_online`."""
        self._stats_on = False
        self._abort_downloads()
        if self.conn and not self.conn.closed:
            try:
                self.conn.close(0, "logout")
            except Exception:
                pass
        if self.ep:
            self.ep.close()
        self.ep = self.conn = None
        self.user, self.peers, self.status = None, [], "offline"
        if announce:
            self.emit("status", status="offline")

    async def logout(self):
        await self._disconnect()

    def _on_conn_close(self, conn, reason):
        if conn is not self.conn:
            return
        log.warning("connection lost: %s", reason)
        self.conn = None
        if self.ep:
            self.ep.close()
            self.ep = None
        self.peers = []
        self._abort_downloads()
        if self._auth_fut and not self._auth_fut.done():
            self._auth_fut.set_exception(AuthError(reason))
        if self._want_online and "logged in from another place" not in reason:
            self.status = "reconnecting"
            self.emit("status", status=self.status, reason=reason)
            if self._reconnect_task is None or self._reconnect_task.done():
                self._reconnect_task = asyncio.ensure_future(self._reconnect())
        else:
            self.status, self.user = "offline", None
            self._want_online = False
            self.emit("status", status="offline", reason=reason)

    async def _reconnect(self):
        # Thử kết nối lại với backoff luỹ thừa 1s -> 15s. Lỗi tạm thời thì thử mãi; chỉ dừng khi bị server
        # từ chối thông tin đăng nhập (AuthRejected) hoặc người dùng chủ động đăng xuất / đăng nhập lại.
        delay = 1.0
        while self._want_online:
            await asyncio.sleep(delay)
            try:
                await self._connect()
                self.emit("notice", level="info", text="Reconnected to server")
                return
            except AuthRejected as exc:
                # Server từ chối thông tin đăng nhập: dừng hẳn và báo UI. (Trước đây vòng lặp thoát nhưng UI
                # vẫn hiển thị "reconnecting" mãi mãi.)
                self.emit("notice", level="error", text=f"Re-login failed: {exc}")
                self._want_online = False
                self.status, self.user = "offline", None
                self.emit("status", status="offline", reason=f"Re-login failed: {exc}")
                return
            except Exception as exc:                  # lỗi tạm thời (mạng, timeout, đứt giữa chừng): thử lại
                log.info("reconnect failed: %s", exc)
            delay = min(delay * 2, 15)
            self.status = "reconnecting"
            self.emit("status", status=self.status)

    async def _stats_loop(self):
        try:
            while self._stats_on:
                await asyncio.sleep(1.0)
                if self.conn and not self.conn.closed:
                    self.emit("stats", stats=self.conn.stats())
        finally:
            if self._stats_task is asyncio.current_task():
                self._stats_task = None

    # ------------------------------------------------------------ receiving
    def _on_data(self, conn, sid, data, fin):
        try:
            if sid == 1:
                self._ctrl.feed(data)
                while (m := self._ctrl.pop()) is not None:
                    self._on_ctrl(m)
                return
            st = self.rx.get(sid)
            if st is None:
                st = self.rx[sid] = {"kind": None, "buf": MsgBuffer()}
            if st["kind"] is None:
                st["buf"].feed(data)
                hdr = st["buf"].pop()
                if hdr is None:
                    return
                if hdr["t"] == "MSG":
                    st["kind"] = "msg"
                    self._on_msg(hdr)
                elif hdr["t"] == "FILE":
                    self._file_start(st, hdr)
                    self._file_data(st, fin)
                else:
                    raise ProtocolError("unexpected message")
            elif st["kind"] == "file":
                st["buf"].feed(data)
                self._file_data(st, fin)
            if fin:
                self.rx.pop(sid, None)
        except ProtocolError as exc:
            log.warning("protocol error: %s", exc)
            conn.close(5, str(exc))

    def _on_ctrl(self, m):
        t = m["t"]
        if t == "AUTH_OK" and self._auth_fut and not self._auth_fut.done():
            self._auth_fut.set_result(m)
        elif t == "AUTH_FAIL" and self._auth_fut and not self._auth_fut.done():
            self._auth_fut.set_exception(AuthRejected(m.get("msg", "authentication failed")))
        elif t == "PEERS":
            self.peers = m["peers"]
            self.emit("peers", peers=self.peers)
        elif t == "SENT":
            item = self._midx.get(m.get("ref"))
            if item:
                item.update(status="sent", n=m.get("n"), ts=m.get("ts", item["ts"]))   # server clock = common ordering
            self.emit("sent", ref=m.get("ref"), n=m.get("n"), ts=m.get("ts"))
        elif t == "ERR":
            ref, text = m.get("ref", ""), m.get("msg", "error")
            self.aborted.add(ref)
            self._fail(ref, text)
            self.emit("error", ref=ref, text=text)

    def _fail(self, ref, text):
        """Mark a message or a file transfer as failed (state survives a UI reload)."""
        item = self._midx.get(ref) or self._fidx.get(ref)
        if item and item.get("status") != "done":
            item.update(status="failed", error=text)

    def _on_msg(self, m):
        item = {"id": m.get("id"), "from": m.get("from"), "to": m.get("to"), "text": m.get("text", ""),
                "ts": m.get("ts", time.time()), "mine": False, "status": "sent"}
        self._remember(item, self._midx, self.history)
        self.emit("msg", **item)

    def _unique_path(self, name):
        # Tránh ghi đè file đã nhận trước đó (cùng tên từ hai người khác nhau): thêm " (n)" trước phần mở rộng.
        # Cũng kiểm tra cả file `.part` để hai lần nhận song song không tranh nhau cùng một đường dẫn tạm.
        base, ext = os.path.splitext(safe_filename(name))
        path, n = os.path.join(self.download_dir, base + ext), 1
        while os.path.exists(path) or os.path.exists(path + ".part"):
            path = os.path.join(self.download_dir, f"{base} ({n}){ext}")
            n += 1
        return path

    def _file_start(self, st, hdr):
        try:
            size = int(hdr["size"])
        except (KeyError, TypeError, ValueError):
            raise ProtocolError("invalid file header")
        if size < 0:
            raise ProtocolError("invalid file size")
        path = self._unique_path(hdr.get("name", "file"))
        st.update(kind="file", hdr=hdr, path=path, fh=open(path + ".part", "wb"), sha=hashlib.sha256(),
                  remaining=size, got=0, last_emit=0.0, trailer=None)
        item = {"id": hdr.get("id"), "from": hdr.get("from"), "to": self.user, "name": os.path.basename(path),
                "size": st["remaining"], "ts": time.time(), "mine": False, "status": "active", "done": 0, "dir": "down"}
        self._remember(item, self._fidx, self.files)
        st["item"] = item
        self.emit("file_start", id=item["id"], name=item["name"], size=item["size"], frm=item["from"],
                  to=self.user, dir="down")

    def _file_data(self, st, fin):
        # Thân file là `size` byte thô, theo sau là thông điệp FILE_END chứa SHA-256. Ghi theo từng mảnh
        # (không giữ cả file trong RAM) và chỉ phát tiến độ tối đa 10 lần/giây để không làm nghẽn UI.
        # `st["buf"]` có thể chứa cả header, thân và trailer trong cùng một lần callback nên hàm này luôn
        # lấy tối đa `remaining` byte rồi mới thử đọc FILE_END.
        buf = st["buf"]
        if st["remaining"] > 0 and len(buf.buf):
            chunk = buf.take(min(st["remaining"], len(buf.buf)))
            st["fh"].write(chunk)
            st["sha"].update(chunk)
            st["remaining"] -= len(chunk)
            st["got"] += len(chunk)
            st["item"]["done"] = st["got"]
            now = time.monotonic()
            if now - st["last_emit"] > 0.1:
                st["last_emit"] = now
                self.emit("file_progress", id=st["hdr"].get("id"), done=st["got"], size=int(st["hdr"]["size"]), dir="down")
        if st["remaining"] == 0 and st["trailer"] is None:
            st["trailer"] = buf.pop()
        if fin:
            self._file_finish(st)

    def _file_finish(self, st):
        # Chỉ chấp nhận file khi đủ byte VÀ băm khớp; ngược lại xoá file tạm (không để lại file hỏng cho người dùng).
        st["fh"].close()
        hdr, path = st["hdr"], st["path"]
        ok = st["remaining"] == 0 and st["trailer"] and st["trailer"].get("sha256") == st["sha"].hexdigest()
        item = st["item"]
        if ok:
            os.replace(path + ".part", path)
            item.update(status="done", done=item["size"], ts=time.time())
            self.emit("file_received", id=item["id"], **{k: item[k] for k in ("from", "name", "size", "ts")})
        else:
            try:
                os.remove(path + ".part")
            except OSError:
                pass
            text = f"File '{hdr.get('name')}' is corrupted or incomplete"
            self._fail(item["id"], text)
            self.emit("error", ref=hdr.get("id"), text=text)

    # ------------------------------------------------------------ sending
    def _require(self):
        if not self.conn or self.conn.closed or self.status != "online":
            raise ConnectionError("not connected to the server")
        return self.conn

    def send_message(self, to, text):
        # Mỗi tin là một stream riêng (mở + FIN ngay) nên không phải chờ tin trước hay file lớn gửi xong.
        # `mid` do client sinh chỉ để đối chiếu SENT/ERR và hiển thị trạng thái gửi.
        conn = self._require()
        mid = uuid.uuid4().hex[:12]
        sid = conn.open_stream(0)
        conn.send(sid, pack({"t": "MSG", "id": mid, "to": to, "text": text}), fin=True)
        item = {"id": mid, "from": self.user, "to": to, "text": text, "ts": time.time(), "mine": True,
                "status": "pending"}
        self._remember(item, self._midx, self.history)
        self.emit("msg", **item)
        return mid

    async def send_file(self, to, name, size, chunks, fid=None):
        """`chunks` is an async iterator of bytes (exactly `size` bytes in total)."""
        # Mỗi file một stream ưu tiên thấp (1). `conn.drain` tạo back-pressure: tạm dừng đọc từ trình duyệt
        # khi bộ đệm gửi đầy, nên RAM không tăng theo kích thước file. Tiến độ tính theo byte ĐÃ ĐƯỢC ACK.
        conn = self._require()
        fid = fid or uuid.uuid4().hex[:12]
        sid = conn.open_stream(1)
        header = pack({"t": "FILE", "id": fid, "to": to, "name": name, "size": size})
        conn.send(sid, header)
        done_fut = conn.send_done(sid)
        item = {"id": fid, "from": self.user, "to": to, "name": name, "size": size, "ts": time.time(),
                "mine": True, "status": "active", "done": 0, "dir": "up"}
        self._remember(item, self._fidx, self.files)
        self.emit("file_start", id=fid, name=name, size=size, frm=self.user, to=to, dir="up")

        async def progress():
            while True:
                await asyncio.sleep(0.2)
                off = conn.acked_offset(sid)
                got = size if off is None else max(0, off - len(header))
                item["done"] = min(got, size)
                self.emit("file_progress", id=fid, done=item["done"], size=size, dir="up")
        ptask = asyncio.ensure_future(progress())
        sha, sent, finished = hashlib.sha256(), 0, False
        try:
            async for chunk in chunks:
                if fid in self.aborted:
                    break
                sha.update(chunk)
                sent += len(chunk)
                conn.send(sid, chunk)
                await conn.drain(sid)
            if fid in self.aborted:
                conn.send(sid, b"", fin=True)
                raise ConnectionError("transfer rejected by server")
            if sent != size:
                raise ValueError("size mismatch")
            conn.send(sid, pack({"t": "FILE_END", "sha256": sha.hexdigest()}), fin=True)
            if not await done_fut:
                raise ConnectionError("connection lost during transfer")
            finished = True
            item.update(status="done", done=size, ts=time.time())
            self.emit("file_progress", id=fid, done=size, size=size, dir="up")
            self.emit("file_sent", id=fid, name=name, size=size, to=to)
        except BaseException as exc:
            if not finished and item["status"] != "failed":
                self._fail(fid, str(exc) or "transfer failed")
                self.emit("error", ref=fid, text=str(exc) or "transfer failed")
            raise
        finally:
            ptask.cancel()
            self.aborted.discard(fid)              # dọn cờ huỷ để tập `aborted` không phình mãi
            if not finished and not conn.closed:
                try:                       # FIN without FILE_END: receiver drops its .part file instead of waiting forever
                    conn.send(sid, b"", fin=True)
                except Exception:
                    pass
        return fid

    def open_download(self, name):
        # `safe_filename` bỏ mọi thành phần đường dẫn, nên tên do trình duyệt gửi lên không thể thoát khỏi
        # thư mục downloads (chống path traversal qua /api/download/..%2f..).
        path = os.path.join(self.download_dir, safe_filename(name))
        return path if os.path.isfile(path) else None
