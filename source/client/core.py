"""Lõi client: logic mạng + giao thức ứng dụng. Không có mã UI ở đây (xem gateway.py / web/).

Lớp ClientCore giữ kết nối tới server, tự kết nối lại khi mất mạng, lưu lịch sử tin nhắn/tệp trong bộ nhớ
và phát sự kiện (emit) cho UI. File nhận được ghi vào `*.part` rồi đổi tên sau khi kiểm tra SHA-256;
file gửi đi theo P2P trực tiếp (một người, hoặc fan-out tới từng người trong chat chung), không qua server.
Byte dành cho người đang offline nằm trong outbox của người gửi và được đẩy P2P khi họ đăng nhập lại.
"""
import asyncio
import hashlib
import json
import logging
import os
import re
import socket
import time
import uuid

from common import crypto
from common.fsutil import atomic_write_json
from common.protocol import MAX_TEXT, PROTO_VERSION, TCP_HELLO_TIMEOUT, MsgBuffer, ProtocolError, pack, safe_filename
from common.transport import Endpoint

log = logging.getLogger("collabnet.client")
FILE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")   # fid dùng làm tên file trong outbox: không được chứa đường dẫn


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
        # --- P2P: mỗi client vừa là người nhận kết nối trực tiếp từ client khác (file không đi qua server)
        self._p2p_ep = None                      # Endpoint UDP nhận kết nối P2P
        self.p2p_fp = ""                         # fingerprint khoá Ed25519 của client này (công bố qua server)
        self._p2p_conns: dict[str, tuple] = {}   # user -> (Connection, fingerprint đã xác minh)
        self._p2p_rx: dict[object, dict] = {}    # Connection P2P -> {sid: trạng thái stream đang nhận}
        self._p2p_lock = asyncio.Lock()          # mỗi Endpoint chỉ bắt tay được một kết nối tại một thời điểm
        self._ctrl_sid = None                    # stream điều khiển client -> server (0)
        self._pending_history = None             # HISTORY đến trước khi biết `user` (xử lý sau khi đăng nhập xong)
        self._midx: dict[str, dict] = {}        # id tin nhắn -> mục lịch sử (trạng thái gửi)
        self._fidx: dict[str, dict] = {}        # id file -> mục file (tiến độ / trạng thái)
        self.max_file = None                    # giới hạn dung lượng file của server (byte), biết khi đăng nhập
        self.subscribers: set[asyncio.Queue] = set()
        self.rx: dict[int, dict] = {}
        self.aborted: set[str] = set()
        self._outbox: dict[str, dict] = {}       # fid -> file đã spool, chờ đẩy P2P (kể cả chat chung)
        self._file_locks: dict[str, asyncio.Lock] = {}
        self._waiters: dict[str, asyncio.Future] = {}  # id -> FILE_OK / ERR từ server
        self._flush_task = None
        self._received: dict[str, str] = {}      # fid -> tên file đã lưu trong downloads
        self._load_received()
        self._auth_fut = None
        self._ctrl = MsgBuffer()
        self._want_online = False
        self._stats_on = False
        self._reconnect_task = self._stats_task = None
        self.status = "offline"

    # ------------------------------------------------------------ sự kiện
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
        # Ảnh chụp để UI dựng lại màn hình sau khi tải lại trang; chỉ gửi phần đuôi lịch sử để payload không phình.
        return {"status": self.status, "user": self.user, "peers": self.peers, "history": self.history[-300:],
                "files": self.files[-100:], "stats": self.conn.stats() if self.conn else None, "cc": self.cc,
                "max_file": self.max_file}

    def _remember(self, item, index, store):
        """Giữ lịch sử trong RAM có giới hạn (tin nhắn / lượt truyền file) để UI dựng lại sau khi tải lại trang."""
        store.append(item)
        index[item["id"]] = item
        if len(store) > 2000:
            old = store.pop(0)
            index.pop(old["id"], None)

    # ------------------------------------------------------------ quản lý kết nối
    def _verify_server(self, host, port):
        # TOFU: lần đầu ghim fingerprint khoá server; lần sau khác -> từ chối (chống MITM).
        def check(pub: bytes):
            fp, key = crypto.fingerprint(pub), f"{host}:{port}"
            known = {}
            if os.path.exists(self.known_hosts):
                with open(self.known_hosts, encoding="utf-8") as fh:
                    known = json.load(fh)
            if key not in known:                                  # tin ở lần gặp đầu tiên (TOFU)
                known[key] = fp
                atomic_write_json(self.known_hosts, known)        # ghi nguyên tử: không hỏng file pin khi crash
                self.emit("notice", level="info", text=f"New server pinned: {fp}")
            elif known[key] != fp:
                raise ConnectionError(f"SERVER KEY CHANGED for {key} (possible man-in-the-middle). "
                                      f"Expected {known[key]}, got {fp}")
        return check

    async def login(self, host, port, user, password):
        await self._disconnect(announce=False)
        # Lấy lịch sử từ server, tránh lẫn hội thoại của người dùng trước đó trên cùng tiến trình.
        self._clear_chat()
        self.creds = (host, int(port), user, password)
        await self._connect()
        self._want_online = True

    async def _connect(self):
        host, port, user, password = self.creds
        self.status = "connecting"
        self.emit("status", status=self.status)
        infos = await self.loop.getaddrinfo(host, port, family=socket.AF_INET, type=socket.SOCK_STREAM)
        addr = infos[0][4]
        try:
            ack = await self._tcp_handshake(addr, user)
        except BaseException:
            self.status = "offline"
            self.emit("status", status=self.status)
            raise
        addr = (addr[0], ack["udp_port"])           # cổng UDP do server báo trong ACK
        self.emit("notice", level="info", text=f"TCP handshake OK: server ACK (UDP port {ack['udp_port']})")
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
        sid = self._ctrl_sid = conn.open_stream(0)
        # Công bố cổng + khoá P2P: client khác dùng thông tin này để kết nối trực tiếp (server chỉ chuyển tiếp).
        p2p_port = self._p2p_endpoint().addr[1]
        conn.send(sid, pack({"t": "AUTH", "user": user, "pass": password,
                             "p2p_port": p2p_port, "p2p_fp": self.p2p_fp}))
        try:
            res = await asyncio.wait_for(self._auth_fut, 8)
        except BaseException:
            # Chỉ dọn kết nối của lần _connect này và KHÔNG tắt `_want_online`: lỗi xác thực tạm thời
            # (timeout, rớt mạng giữa chừng) không được làm vòng tự kết nối lại dừng hẳn.
            await self._abandon(ep, conn)
            raise
        self.user, self.peers, self.status = res["user"], res["peers"], "online"
        self.max_file = res.get("max_file")
        if self._pending_history is not None:     # HISTORY có thể tới ngay sau AUTH_OK, trước khi biết tên mình
            items, self._pending_history = self._pending_history, None
            self._restore_history(items)
        self.emit("status", status=self.status, user=self.user)
        self.emit("peers", peers=self.peers)
        self._load_outbox()
        self._schedule_flush()
        self._stats_on = True
        if self._stats_task is None or self._stats_task.done():
            self._stats_task = asyncio.ensure_future(self._stats_loop())

    async def _tcp_handshake(self, addr, user):
        """Bước 2 của đề: kết nối TCP tới server, gửi HELLO, chờ HELLO_ACK rồi đóng TCP.

        Kiểm tra server có sống và cùng phiên bản giao thức trước khi mở kết nối UDP mã hoá.
        Trả về thông điệp ACK (có `udp_port`, `fp`); lỗi -> ConnectionError có lý do rõ ràng.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        try:
            async def exchange():
                await self.loop.sock_connect(sock, addr)
                await self.loop.sock_sendall(sock, pack({"t": "HELLO", "proto": PROTO_VERSION, "user": user}))
                buf = MsgBuffer()
                while (m := buf.pop()) is None:
                    data = await self.loop.sock_recv(sock, 4096)
                    if not data:
                        raise EOFError
                    buf.feed(data)
                return m
            try:
                ack = await asyncio.wait_for(exchange(), TCP_HELLO_TIMEOUT)
            except asyncio.TimeoutError:
                raise ConnectionError("TCP handshake timeout: server did not acknowledge")
            except EOFError:
                raise ConnectionError("TCP handshake: server closed the connection before ACK")
            except ProtocolError as exc:
                raise ConnectionError(f"TCP handshake: bad reply ({exc})")
            except OSError as exc:              # gồm cả ConnectionRefusedError / ConnectionResetError
                raise ConnectionError(f"cannot reach server over TCP {addr[0]}:{addr[1]}: {exc.strerror or exc}")
            if ack.get("t") != "HELLO_ACK":
                raise ConnectionError(f"TCP handshake rejected: {ack.get('msg', ack.get('t'))}")
            try:
                udp_port = int(ack.get("udp_port"))
            except (TypeError, ValueError):
                udp_port = 0
            if not 0 < udp_port < 65536:
                raise ConnectionError("TCP handshake: invalid UDP port in ACK")
            ack["udp_port"] = udp_port
            log.info("TCP handshake with %s:%d acknowledged", *addr)
            return ack
        finally:
            sock.close()

    def _abort_downloads(self):
        self._abort_rx(self.rx)

    def _abort_rx(self, rx, reason="connection lost"):
        """Huỷ mọi file đang nhận dở trên một kết nối vừa đứt: đóng file, xoá `.part`, đánh dấu thất bại.

        Trước đây kết nối P2P đứt giữa chừng chỉ bỏ trạng thái nhận: file handle bị rò, `.part` nằm lại
        trong downloads và thẻ file kẹt ở "active" mãi mãi.
        """
        for st in list(rx.values()):
            fh = st.get("fh")
            if fh and not fh.closed:
                fh.close()
            part = st.get("path")
            if part:
                try:
                    os.remove(part + ".part")
                except OSError:
                    pass
            item, hdr = st.get("item"), st.get("hdr") or {}
            if item is not None and item.get("status") != "done":
                text = f"File '{hdr.get('name', item.get('name'))}' was interrupted ({reason})"
                self._fail(item["id"], text)
                self.emit("error", ref=item["id"], text=text)
        rx.clear()

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
        self._ctrl_sid = None
        for fut in list(self._waiters.values()):
            if not fut.done():
                fut.set_exception(ConnectionError("connection lost"))
        self._waiters.clear()
        self._drop_p2p_conns()
        self.user, self.peers, self.status = None, [], "offline"
        if announce:
            self.emit("status", status="offline")

    async def logout(self):
        await self._disconnect()
        self._close_p2p()
        self._clear_chat()                        # lần đăng nhập sau sẽ nhận lại lịch sử từ server

    def _clear_chat(self):
        """Xoá hội thoại trong RAM (server mới là nơi lưu lịch sử lâu dài)."""
        self.history.clear()
        self.files.clear()
        self._midx.clear()
        self._fidx.clear()
        self.aborted.clear()
        self._pending_history = None

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

    # ------------------------------------------------------------ peer-to-peer
    def _p2p_endpoint(self):
        """Endpoint nhận kết nối trực tiếp từ client khác. Khoá Ed25519 riêng được công bố qua server để
        người gửi xác minh đúng máy nhận (không thể giả mạo peer khác)."""
        if self._p2p_ep is None:
            identity = crypto.load_or_create_identity(os.path.join(self.state_dir, "client_identity.key"))
            ep = Endpoint(self.loop, ("0.0.0.0", 0), identity=identity, cc=self.cc,
                          sim_loss=self.sim_loss, sim_delay=self.sim_delay)
            ep.on_accept = self._on_p2p_accept
            self._p2p_ep, self.p2p_fp = ep, crypto.fingerprint(crypto.public_bytes(identity))
        return self._p2p_ep

    def _on_p2p_accept(self, conn):
        rx = self._p2p_rx[conn] = {}
        conn.on_stream_data = lambda c, sid, data, fin: self._on_p2p_data(c, rx, sid, data, fin)
        conn.on_close = lambda c, reason: self._abort_rx(self._p2p_rx.pop(c, {}), reason)

    def _on_p2p_data(self, conn, rx, sid, data, fin):
        # Chỉ file đi trên kết nối P2P; dùng chung logic ghép file với luồng nhận từ server.
        try:
            self._on_stream(rx, sid, data, fin)
        except ProtocolError as exc:
            log.warning("protocol error on peer connection: %s", exc)
            conn.close(5, str(exc))

    def _drop_p2p_conns(self):
        for conn, _fp in list(self._p2p_conns.values()):
            try:
                conn.close(0, "peer session ended")
            except Exception:
                pass
        self._p2p_conns.clear()

    def _close_p2p(self):
        self._drop_p2p_conns()
        for rx in list(self._p2p_rx.values()):
            self._abort_rx(rx, "logged out")
        self._p2p_rx.clear()
        if self._p2p_ep is not None:
            self._p2p_ep.close()
            self._p2p_ep = None

    def _sync_p2p_cache(self):
        """Bỏ kết nối P2P cũ: người đó offline, hoặc khoá của họ đã đổi (đăng nhập lại / máy khác)."""
        live = {p.get("user"): p.get("p2p_fp", "") for p in self.peers}
        for user, (conn, fp) in list(self._p2p_conns.items()):
            if conn.closed or live.get(user) != fp:
                try:
                    conn.close(0, "peer session changed")
                except Exception:
                    pass
                self._p2p_conns.pop(user, None)

    async def _refresh_peers(self, user, timeout=2.0):
        """Xin danh sách peer mới nhất khi thông tin P2P của `user` chưa đến (PEERS đang trên đường)."""
        deadline = self.loop.time() + timeout
        while self.status == "online" and self.loop.time() < deadline:
            if any(p.get("user") == user and p.get("p2p_port") for p in self.peers):
                return
            if self.conn and not self.conn.closed and self._ctrl_sid is not None:
                self.conn.send(self._ctrl_sid, pack({"t": "LIST"}))
            await asyncio.sleep(0.1)

    async def _p2p_connect(self, user):
        """Kết nối TRỰC TIẾP tới client của `user`; khoá phải khớp fingerprint server đã công bố."""
        peer = next((p for p in self.peers if p.get("user") == user), None)
        if peer is None or not peer.get("p2p_port") or not peer.get("p2p_fp"):
            await self._refresh_peers(user)
            peer = next((p for p in self.peers if p.get("user") == user), None)
        if peer is None:
            raise ConnectionError(f"user '{user}' is not online")
        try:
            port = int(peer.get("p2p_port") or 0)
        except (TypeError, ValueError):
            port = 0
        fp = str(peer.get("p2p_fp") or "")
        if not 0 < port < 65536 or not fp:
            raise ConnectionError(f"user '{user}' does not accept peer-to-peer transfers")
        cached = self._p2p_conns.get(user)
        if cached is not None and not cached[0].closed and cached[1] == fp:
            return cached[0]
        ep, addr = self._p2p_endpoint(), (peer.get("ip") or "127.0.0.1", port)

        def verify(pub: bytes):
            if crypto.fingerprint(pub) != fp:
                raise ConnectionError(f"peer key mismatch for '{user}' (possible man-in-the-middle)")

        async with self._p2p_lock:
            cached = self._p2p_conns.get(user)
            if cached is not None and not cached[0].closed and cached[1] == fp:
                return cached[0]
            conn = await ep.connect(addr, verify=verify)
        self._p2p_conns[user] = (conn, fp)
        return conn

    # ------------------------------------------------------------ nhận
    def _on_data(self, conn, sid, data, fin):
        try:
            if sid == 1:
                self._ctrl.feed(data)
                while (m := self._ctrl.pop()) is not None:
                    self._on_ctrl(m)
                return
            self._on_stream(self.rx, sid, data, fin)
        except ProtocolError as exc:
            log.warning("protocol error: %s", exc)
            conn.close(5, str(exc))

    def _on_stream(self, rx, sid, data, fin):
        st = rx.get(sid)
        if st is None:
            st = rx[sid] = {"kind": None, "buf": MsgBuffer()}
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
            rx.pop(sid, None)

    def _on_ctrl(self, m):
        t = m["t"]
        if t == "AUTH_OK" and self._auth_fut and not self._auth_fut.done():
            self._auth_fut.set_result(m)
        elif t == "AUTH_FAIL" and self._auth_fut and not self._auth_fut.done():
            self._auth_fut.set_exception(AuthRejected(m.get("msg", "authentication failed")))
        elif t == "PEERS":
            self.peers = m["peers"]
            self._sync_p2p_cache()
            self.emit("peers", peers=self.peers)
            self._schedule_flush()                 # người vừa online: đẩy file P2P còn nằm trong outbox
        elif t == "FILE_OK":
            fut = self._waiters.pop(m.get("ref"), None)
            if fut is not None and not fut.done():
                fut.set_result(m)
        elif t == "HISTORY":
            items = m.get("items") or []
            if self.user is None:
                self._pending_history = (self._pending_history or []) + items
            else:
                self._restore_history(items)
        elif t == "SENT":
            item = self._midx.get(m.get("ref"))
            if item:
                item.update(status="sent", n=m.get("n"), ts=m.get("ts", item["ts"]))   # giờ server làm chuẩn sắp xếp chung
            self.emit("sent", ref=m.get("ref"), n=m.get("n"), ts=m.get("ts"))
        elif t == "ERR":
            ref, text = m.get("ref", ""), m.get("msg", "error")
            fut = self._waiters.pop(ref, None)
            if fut is not None and not fut.done():
                fut.set_exception(ConnectionError(text))
            self.aborted.add(ref)
            self._fail(ref, text)
            self.emit("error", ref=ref, text=text)

    def _fail(self, ref, text):
        """Đánh dấu tin nhắn hoặc lượt truyền file là thất bại (trạng thái còn sau khi tải lại UI)."""
        item = self._midx.get(ref) or self._fidx.get(ref)
        if item and item.get("status") != "done":
            item.update(status="failed", error=text)

    def _on_msg(self, m):
        item = {"id": m.get("id"), "from": m.get("from"), "to": m.get("to"), "text": m.get("text", ""),
                "ts": m.get("ts", time.time()), "mine": False, "status": "sent"}
        self._remember(item, self._midx, self.history)
        self.emit("msg", **item)

    def _restore_history(self, items):
        """Nạp lại lịch sử server gửi sau khi đăng nhập (tin nhắn và thẻ file lúc đang offline)."""
        restored = []
        for rec in items:
            if not isinstance(rec, dict):
                continue
            if rec.get("kind") == "file":
                self._restore_file(rec, restored)
            else:
                self._restore_message(rec, restored)
        if restored:
            self.history.sort(key=lambda it: it.get("ts", 0))
            self.files.sort(key=lambda it: it.get("ts", 0))
        self.emit("history", items=restored)      # luôn phát (kể cả rỗng) để UI biết đã nạp xong lịch sử

    def _restore_message(self, rec, restored):
        mid, frm, to = rec.get("id"), rec.get("from"), rec.get("to")
        if not mid or not frm or not to:
            return
        old = self._midx.get(mid)
        if old is not None:                       # tin đã có trong RAM (tự kết nối lại): chỉ đồng bộ giờ
            old.update(status="sent", ts=rec.get("ts", old["ts"]))
            return
        try:
            ts = float(rec.get("ts") or time.time())
        except (TypeError, ValueError):
            ts = time.time()
        item = {"id": mid, "from": str(frm), "to": str(to), "text": str(rec.get("text") or "")[:MAX_TEXT],
                "ts": ts, "mine": str(frm) == self.user, "status": "sent"}
        self._remember(item, self._midx, self.history)
        restored.append(item)

    def _restore_file(self, rec, restored):
        """Thẻ file từ lịch sử. Byte tới sau bằng P2P nếu máy người gửi còn giữ outbox."""
        fid, frm, to = rec.get("id"), rec.get("from"), rec.get("to")
        if not fid or not frm or not to or self._fidx.get(fid) is not None:
            return
        try:
            ts = float(rec.get("ts") or time.time())
            size = int(rec.get("size") or 0)
        except (TypeError, ValueError):
            ts, size = time.time(), 0
        mine = str(frm) == self.user
        saved = self._received.get(str(fid))
        on_disk = bool(saved) and os.path.isfile(os.path.join(self.download_dir, saved))
        name = saved if on_disk else safe_filename(rec.get("name") or "file")
        item = {"id": str(fid), "from": str(frm), "to": str(to), "name": name, "size": size, "ts": ts,
                "mine": mine, "status": "done" if mine or on_disk else "queued",
                "done": size if mine or on_disk else 0, "dir": "up" if mine else "down"}
        self._remember(item, self._fidx, self.files)
        restored.append({**item, "kind": "file"})

    def _load_received(self):
        path = os.path.join(self.state_dir, "received.json")
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return
        if isinstance(data, dict):
            self._received = {str(k): str(v) for k, v in data.items() if v}

    def _remember_download(self, fid, name):
        if not fid or not name:
            return
        self._received[str(fid)] = name
        try:
            atomic_write_json(os.path.join(self.state_dir, "received.json"), self._received)
        except OSError:
            log.exception("cannot write received file index")

    def _outbox_dir(self):
        path = os.path.join(self.state_dir, "outbox")
        os.makedirs(path, exist_ok=True)
        return path

    def _outbox_path(self, fid):
        return os.path.join(self._outbox_dir(), fid + ".bin")

    def _load_outbox(self):
        """Nạp file còn phải đẩy P2P (người gửi đăng nhập lại sau khi người nhận từng offline)."""
        index = os.path.join(self._outbox_dir(), "index.json")
        try:
            with open(index, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return
        if not isinstance(data, dict):
            return
        for fid, meta in data.items():
            if not isinstance(meta, dict) or not FILE_ID_RE.match(str(fid)):
                continue
            path = self._outbox_path(str(fid))
            if not os.path.isfile(path):
                continue
            self._outbox[str(fid)] = {
                "id": str(fid), "to": str(meta.get("to") or "*"), "name": str(meta.get("name") or "file"),
                "size": int(meta.get("size") or 0), "sha256": str(meta.get("sha256") or ""),
                "delivered": set(meta.get("delivered") or []), "path": path,
            }

    def _save_outbox_index(self):
        index = {fid: {"to": m["to"], "name": m["name"], "size": m["size"], "sha256": m["sha256"],
                       "delivered": sorted(m["delivered"])}
                 for fid, m in self._outbox.items()}
        try:
            atomic_write_json(os.path.join(self._outbox_dir(), "index.json"), index)
        except OSError:
            log.exception("cannot write file outbox index")

    def _drop_spool(self, fid):
        meta = self._outbox.pop(fid, None)
        if meta is not None:
            try:
                os.remove(meta["path"])
            except OSError:
                pass
        self._save_outbox_index()

    def _schedule_flush(self):
        if self.status != "online":
            return
        if self._flush_task is None or self._flush_task.done():
            self._flush_task = asyncio.ensure_future(self._flush_all())

    def _online_targets(self, to):
        """Người đang online và có cổng P2P. Chat chung là mọi người trừ chính mình."""
        def ready(peer):
            user = peer.get("user")
            return bool(user) and user != self.user and peer.get("p2p_port") and peer.get("p2p_fp")

        if to == "*":
            return [p["user"] for p in self.peers if ready(p)]
        peer = next((p for p in self.peers if p.get("user") == to), None)
        return [to] if peer is not None and ready(peer) else []

    async def _announce_file(self, meta):
        """Báo server ghi thẻ file (không kèm byte) để người offline thấy khi đăng nhập lại."""
        fut = self.loop.create_future()
        self._waiters[meta["id"]] = fut
        self.conn.send(self._ctrl_sid, pack({
            "t": "FILE_LOG", "id": meta["id"], "to": meta["to"], "name": meta["name"],
            "size": meta["size"], "sha256": meta["sha256"],
        }))
        try:
            await asyncio.wait_for(fut, 8)
        except asyncio.TimeoutError:
            self._waiters.pop(meta["id"], None)
            raise ConnectionError("server did not accept the file")

    async def _p2p_push(self, user, meta, item=None):
        """Đẩy một file đã nằm trên đĩa sang `user` bằng kết nối P2P."""
        conn = await self._p2p_connect(user)
        sid = conn.open_stream(1)
        header = pack({"t": "FILE", "id": meta["id"], "from": self.user, "to": meta["to"],
                       "name": meta["name"], "size": meta["size"]})
        conn.send(sid, header)
        done_fut = conn.send_done(sid)
        size = meta["size"]
        sent = 0
        with open(meta["path"], "rb") as fh:
            while True:
                chunk = fh.read(65536)
                if not chunk:
                    break
                if meta["id"] in self.aborted:
                    conn.send(sid, b"", fin=True)
                    raise ConnectionError("transfer aborted")
                sent += len(chunk)
                conn.send(sid, chunk)
                await conn.drain(sid)
                if item is not None and item.get("status") != "done":
                    item["done"] = min(sent, size)
                    item["status"] = "active"
                    self.emit("file_progress", id=meta["id"], done=item["done"], size=size, dir="up")
        if sent != size:
            conn.send(sid, b"", fin=True)
            raise ConnectionError("spooled file is incomplete")
        conn.send(sid, pack({"t": "FILE_END", "sha256": meta["sha256"]}), fin=True)
        if not await done_fut:
            raise ConnectionError("connection lost during transfer")

    async def _flush_all(self):
        for fid in list(self._outbox):
            try:
                await self._flush_one(fid)
            except Exception:
                log.exception("could not deliver pending file %s", fid)

    async def _flush_one(self, fid):
        meta = self._outbox.get(fid)
        if meta is None or not os.path.isfile(meta["path"]):
            return
        lock = self._file_locks.setdefault(fid, asyncio.Lock())
        async with lock:
            meta = self._outbox.get(fid)
            if meta is None:
                return
            item = self._fidx.get(fid)
            for user in self._online_targets(meta["to"]):
                if user in meta["delivered"]:
                    continue
                try:
                    await self._p2p_push(user, meta, item)
                except Exception as exc:
                    log.info("P2P file %s to %s failed: %s", fid, user, exc)
                    continue
                meta["delivered"].add(user)
            self._save_outbox_index()
            if meta["to"] != "*" and meta["to"] in meta["delivered"]:
                if item is not None and item.get("status") != "done":
                    item.update(status="done", done=meta["size"], ts=time.time())
                    self.emit("file_sent", id=fid, name=meta["name"], size=meta["size"], to=meta["to"])
                self._drop_spool(fid)

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
        dest = "*" if hdr.get("to") == "*" else self.user
        item = self._fidx.get(hdr.get("id"))
        if item is None:
            item = {"id": hdr.get("id"), "from": hdr.get("from"), "to": dest, "name": os.path.basename(path),
                    "size": st["remaining"], "ts": time.time(), "mine": False, "status": "active",
                    "done": 0, "dir": "down"}
            self._remember(item, self._fidx, self.files)
        else:
            item.update(status="active", done=0, dir="down", to=dest, name=os.path.basename(path),
                        size=st["remaining"], error=None)
        st["item"] = item
        self.emit("file_start", id=item["id"], name=item["name"], size=item["size"], frm=item["from"],
                  to=dest, dir="down")

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
            self._remember_download(item["id"], item["name"])
            self.emit("file_received", id=item["id"], **{k: item[k] for k in ("from", "name", "size", "ts")})
        else:
            try:
                os.remove(path + ".part")
            except OSError:
                pass
            text = f"File '{hdr.get('name')}' is corrupted or incomplete"
            self._fail(item["id"], text)
            self.emit("error", ref=hdr.get("id"), text=text)

    # ------------------------------------------------------------ gửi
    def _require(self):
        if not self.conn or self.conn.closed or self.status != "online":
            raise ConnectionError("not connected to the server")
        return self.conn

    def send_message(self, to, text):
        # Mỗi tin là một stream riêng (mở + FIN ngay) nên không phải chờ tin trước hay file lớn gửi xong.
        # `mid` do client tự sinh, chỉ để đối chiếu SENT/ERR và hiển thị trạng thái gửi.
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
        """`chunks` là async iterator các byte (đúng `size` byte tổng cộng).

        File đi TRỰC TIẾP giữa các client (P2P). `to == "*"` gửi vào chat chung: một kết nối P2P tới từng
        người đang online. Người đang offline không nhận byte qua server; byte nằm trong outbox của người
        gửi và được đẩy khi họ xuất hiện lại. Server chỉ nhận thẻ FILE_LOG để hiện file trong lịch sử.
        """
        self._require()                            # vẫn cần online để biết địa chỉ/khoá P2P và ghi lịch sử
        if to != "*" and to == self.user:
            raise ConnectionError("cannot send a file to yourself")
        if self.max_file and size > self.max_file:
            raise ConnectionError(f"invalid or too large file (limit {self.max_file // 2**20} MB)")
        if fid is not None and not FILE_ID_RE.match(str(fid)):
            raise ValueError("invalid file id")
        fid = fid or uuid.uuid4().hex[:12]
        item = {"id": fid, "from": self.user, "to": to, "name": name, "size": size, "ts": time.time(),
                "mine": True, "status": "active", "done": 0, "dir": "up"}
        self._remember(item, self._fidx, self.files)
        self.emit("file_start", id=fid, name=name, size=size, frm=self.user, to=to, dir="up")
        lock = self._file_locks.setdefault(fid, asyncio.Lock())
        async with lock:
            return await self._send_file_locked(to, name, size, chunks, fid, item)

    async def _send_file_locked(self, to, name, size, chunks, fid, item):
        path = self._outbox_path(fid)
        conn = sid = ptask = None
        sha, sent, finished = hashlib.sha256(), 0, False
        primary = None
        try:
            targets = self._online_targets(to)
            unreachable = None
            if targets:
                try:
                    conn = await self._p2p_connect(targets[0])
                    primary = targets[0]
                except Exception as exc:
                    # Người nhận đầu tiên không kết nối được: KHÔNG huỷ cả lượt gửi (trước đây cả nhóm mất file).
                    # Vẫn spool ra outbox, đẩy cho những người còn lại; người này nhận sau khi xuất hiện lại.
                    log.info("P2P connect to %s failed, spooling only: %s", targets[0], exc)
                    unreachable, conn = targets[0], None
            if conn is not None:
                sid = conn.open_stream(1)
                header = pack({"t": "FILE", "id": fid, "from": self.user, "to": to, "name": name, "size": size})
                conn.send(sid, header)
                done_fut = conn.send_done(sid)

                async def progress():
                    while True:
                        await asyncio.sleep(0.2)
                        off = conn.acked_offset(sid)
                        got = size if off is None else max(0, off - len(header))
                        item["done"] = min(got, size)
                        self.emit("file_progress", id=fid, done=item["done"], size=size, dir="up")
                ptask = asyncio.ensure_future(progress())
            with open(path, "wb") as fh:
                async for chunk in chunks:
                    if fid in self.aborted:
                        raise ConnectionError("transfer aborted")
                    sha.update(chunk)
                    sent += len(chunk)
                    fh.write(chunk)
                    if conn is not None:
                        conn.send(sid, chunk)
                        await conn.drain(sid)     # back-pressure: RAM không tăng theo kích thước file
            if sent != size:
                raise ValueError("size mismatch")
            digest = sha.hexdigest()
            delivered = set()
            if conn is not None:
                conn.send(sid, pack({"t": "FILE_END", "sha256": digest}), fin=True)
                if not await done_fut:
                    raise ConnectionError("connection lost during transfer")
                delivered.add(primary)
            meta = {"id": fid, "to": to, "name": name, "size": size, "sha256": digest,
                    "delivered": delivered, "path": path}
            self._outbox[fid] = meta
            self._save_outbox_index()
            await self._announce_file(meta)
            for user in targets:
                if user in (primary, unreachable):
                    continue
                try:
                    await self._p2p_push(user, meta, item)
                except Exception as exc:
                    log.info("P2P file %s to %s failed: %s", fid, user, exc)
                    continue
                meta["delivered"].add(user)
            self._save_outbox_index()
            finished = True
            if to != "*" and to not in meta["delivered"]:
                item.update(status="queued", done=0)
                self.emit("file_queued", id=fid, name=name, size=size, to=to)
            else:
                item.update(status="done", done=size, ts=time.time())
                self.emit("file_progress", id=fid, done=size, size=size, dir="up")
                self.emit("file_sent", id=fid, name=name, size=size, to=to)
                if to != "*":
                    self._drop_spool(fid)          # chat riêng đã tới nơi; chat chung giữ outbox cho người offline
        except BaseException as exc:
            if sent != size:
                self._outbox.pop(fid, None)
                try:
                    os.remove(path)
                except OSError:
                    pass
            elif fid not in self._outbox and os.path.isfile(path):
                # Đã spool đủ nhưng P2P tới người đang online thất bại: giữ file để đẩy lại.
                self._outbox[fid] = {"id": fid, "to": to, "name": name, "size": size,
                                     "sha256": sha.hexdigest(), "delivered": set(), "path": path}
                self._save_outbox_index()
            if not finished and item["status"] != "failed":
                text = str(exc) or "transfer failed"
                self._fail(fid, text)
                self.emit("error", ref=fid, text=text)
            raise
        finally:
            if ptask is not None:
                ptask.cancel()
            self.aborted.discard(fid)              # dọn cờ huỷ để tập `aborted` không phình mãi
            if not finished and conn is not None and sid is not None and not conn.closed:
                try:                       # FIN mà không có FILE_END: bên nhận xoá file .part thay vì chờ mãi
                    conn.send(sid, b"", fin=True)
                except Exception:
                    pass
        return fid

    def open_download(self, name):
        # `safe_filename` bỏ mọi thành phần đường dẫn, nên tên do trình duyệt gửi lên không thể thoát khỏi
        # thư mục downloads (chống path traversal qua /api/download/..%2f..).
        path = os.path.join(self.download_dir, safe_filename(name))
        return path if os.path.isfile(path) else None
