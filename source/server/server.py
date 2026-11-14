"""CollabNet server: authentication, presence tracking, message routing, cut-through file relay.

Run:  python -m server.server --port 9000

Tiếng Việt: server làm 4 việc chính trên một socket UDP duy nhất (asyncio, không thread):
  1. Xác thực (AUTH) và đăng ký tài khoản mới ở lần đăng nhập đầu; mật khẩu lưu dạng PBKDF2 có muối.
  2. Theo dõi presence: ai đang online, IP/port nào, và phát danh sách PEERS khi có thay đổi.
  3. Định tuyến tin nhắn (broadcast "*" hoặc riêng tư), mỗi tin một stream nên không bị chặn bởi file lớn.
  4. Relay file kiểu cut-through: byte nhận từ người gửi được chuyển ngay cho người nhận, có back-pressure
     (giữ lại flow-control credit khi bên nhận chậm) nên server không phải lưu cả file trong RAM.
"""
import argparse
import asyncio
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import crypto
from common.discovery import Beacon
from common.protocol import MAX_TEXT, USERNAME_RE, MsgBuffer, ProtocolError, pack, safe_filename
from common.transport import Endpoint
from server.users import UserStore

log = logging.getLogger("collabnet.server")
RELAY_HIGH = 384 * 1024          # relay back-pressure threshold (bytes buffered towards the receiver)
# Quy ước stream (xem common/protocol.py): client mở stream chẵn (0 = control), server mở stream lẻ (1 = control).


# `UserStore` được tách sang server/users.py; re-export để `from server.server import UserStore` vẫn chạy.
__all__ = ["Server", "Session", "StreamState", "Relay", "UserStore", "amain", "main"]


class Session:
    """Trạng thái phía server của một kết nối client: danh tính, buffer control, các stream đang nhận."""

    def __init__(self, conn):
        self.conn, self.user, self.since = conn, None, time.time()
        self.addr = conn.peer_addr                # địa chỉ lúc chấp nhận (dùng cho log)
        self.ctrl = MsgBuffer()
        self.streams = {}
        self.auth_task = None                     # task xác thực đang chạy (chỉ cho phép một task mỗi kết nối)
        self.ctrl_sid = conn.open_stream(0)      # server->client control stream (id 1)


class StreamState:
    """Trạng thái một stream đang nhận từ client: loại (msg/file), buffer phân tích header, thông tin relay."""

    def __init__(self):
        self.kind, self.buf, self.relay = None, MsgBuffer(), None


class Relay:
    """Một lượt chuyển file đang diễn ra: đích, stream phía đích, kích thước khai báo, số byte đã thấy,
    và lượng flow-control credit đang giữ lại (`held`) khi người nhận chưa kịp tiêu thụ."""

    def __init__(self, dest, dsid, size, fid):
        self.dest, self.dsid, self.size, self.fid, self.seen = dest, dsid, size, fid, 0
        self.held = 0
        self.holding = False


class Server:
    """Điều phối toàn bộ phía server; `by_user` ánh xạ tên người dùng -> Session đã xác thực (mỗi tên một phiên)."""

    def __init__(self, loop, host, port, data_dir, cc="cubic", sim_loss=0.0, sim_delay=0.0,
                 max_file_mb=512, beacon=True):
        os.makedirs(data_dir, exist_ok=True)
        self.loop, self.max_file = loop, max_file_mb * 1024 * 1024
        self.store = UserStore(os.path.join(data_dir, "users.json"))
        identity = crypto.load_or_create_identity(os.path.join(data_dir, "server_identity.key"))
        self.fingerprint = crypto.fingerprint(crypto.public_bytes(identity))
        self.ep = Endpoint(loop, (host, port), identity=identity, cc=cc, sim_loss=sim_loss, sim_delay=sim_delay)
        self.ep.on_accept = self._on_accept
        self.port = self.ep.addr[1]
        self.by_user: dict[str, Session] = {}
        self.beacon = Beacon(loop, self.port, "CollabNet") if beacon else None
        log.info("listening on UDP %s:%d, server key fingerprint %s", host, self.port, self.fingerprint)

    def close(self):
        if self.beacon:
            self.beacon.close()
        self.ep.close()

    # ------------------------------------------------------------ sessions
    def _on_accept(self, conn):
        s = Session(conn)
        conn.on_stream_data = lambda c, sid, data, fin: self._on_data(s, sid, data, fin)
        conn.on_close = lambda c, reason: self._on_close(s, reason)
        self.loop.call_later(10, lambda: (not s.user and not conn.closed) and conn.close(4, "auth timeout"))
        log.info("connection from %s:%d", *s.addr)

    def _on_close(self, s, reason):
        # Chỉ gỡ khỏi `by_user` nếu đó vẫn là session hiện hành của user (đăng nhập nơi khác có thể đã thay thế).
        log.info("connection %s:%d (%s) closed: %s", s.addr[0], s.addr[1], s.user, reason)
        if s.user and self.by_user.get(s.user) is s:
            del self.by_user[s.user]
            self._broadcast_peers()

    def _peers(self):
        # Dùng địa chỉ hiện tại của kết nối (có thể đã đổi nếu client chuyển mạng / NAT rebinding)
        return [{"user": u, "ip": s.conn.peer_addr[0], "port": s.conn.peer_addr[1], "since": s.since}
                for u, s in self.by_user.items()]

    def _send_ctrl(self, s, obj):
        if not s.conn.closed:
            s.conn.send(s.ctrl_sid, pack(obj))

    def _broadcast_peers(self):
        for s in list(self.by_user.values()):
            self._send_ctrl(s, {"t": "PEERS", "peers": self._peers()})

    def _deliver(self, dest, obj) -> bool:
        """Chuyển `obj` cho `dest`, mỗi tin một stream riêng (không bị HoL blocking). False nếu `dest` đã rớt.

        Có khoảng trễ ngắn giữa lúc kết nối bị đóng (`conn.closed`) và lúc `_on_close` gỡ session khỏi
        `by_user`; trong khoảng đó `conn.send` ném ConnectionError. Nếu để lỗi này lan ra `_on_data` thì
        server sẽ đóng nhầm kết nối của NGƯỜI GỬI với lý do "internal error".
        """
        if dest.conn.closed:
            return False
        sid = dest.conn.open_stream(0)
        dest.conn.send(sid, pack(obj), fin=True)
        return True

    # ------------------------------------------------------------ data entry point
    def _on_data(self, s, sid, data, fin):
        # Điểm vào cho mọi dữ liệu stream: stream 0 là control; stream khác chỉ được dùng sau khi xác thực.
        # ProtocolError (client vi phạm giao thức) -> đóng kết nối; lỗi bất ngờ khác -> log + đóng, không làm sập server.
        try:
            if sid == 0:
                return self._on_ctrl(s, data)
            if not s.user:
                raise ProtocolError("not authenticated")
            return self._on_stream(s, sid, data, fin)
        except ProtocolError as exc:
            log.warning("protocol error from %s: %s", s.user or s.addr, exc)
            s.conn.close(5, str(exc))
        except Exception:
            log.exception("internal error")
            s.conn.close(1, "internal error")

    def _on_ctrl(self, s, data):
        s.ctrl.feed(data)
        while (m := s.ctrl.pop()) is not None:
            t = m["t"]
            if t == "AUTH" and not s.user:
                if s.auth_task is not None and not s.auth_task.done():
                    # Hai AUTH chồng nhau trên một kết nối sẽ gắn một session vào hai tên (user "ma" còn mãi
                    # trong `by_user` sau khi session đóng) hoặc tự đá chính mình khỏi `by_user`.
                    raise ProtocolError("authentication already in progress")
                s.auth_task = self.loop.create_task(self._auth(s, m))
            elif not s.user:
                raise ProtocolError("authenticate first")
            elif t == "LIST":
                self._send_ctrl(s, {"t": "PEERS", "peers": self._peers()})
            elif t == "BYE":
                s.conn.close(0, "bye")
            else:
                raise ProtocolError(f"unknown control message {t}")

    async def _auth(self, s, m):
        """Xác thực một session; mọi lỗi bất ngờ được log và đóng kết nối (task chạy nền, không ai await)."""
        try:
            await self._do_auth(s, m)
        except Exception:
            log.exception("authentication failed unexpectedly for %s", s.addr)
            s.conn.close(1, "internal error")

    async def _do_auth(self, s, m):
        user, pw = str(m.get("user", "")), str(m.get("pass", ""))
        if not USERNAME_RE.match(user):
            ok, why = False, "invalid username (2-24 chars: letters, digits, _ . -)"
        else:
            ok, why = await self.loop.run_in_executor(None, self.store.check_or_register, user, pw)
        if s.conn.closed:
            return
        if not ok:
            log.info("auth failed for %r from %s: %s", user, s.addr, why)
            self._send_ctrl(s, {"t": "AUTH_FAIL", "msg": why})
            self.loop.call_later(0.5, s.conn.close, 6, "auth failed")
            return
        old = self.by_user.get(user)
        if old is not None:
            old.conn.close(7, "logged in from another place")
        s.user = user
        self.by_user[user] = s
        log.info("user %s logged in from %s:%d (%s)", user, *s.addr, why)
        self._send_ctrl(s, {"t": "AUTH_OK", "user": user, "peers": self._peers(), "msg": why,
                            "max_file": self.max_file})
        self._broadcast_peers()

    # ------------------------------------------------------------ message / file streams
    def _on_stream(self, s, sid, data, fin):
        # Stream tin nhắn/file: thông điệp đầu tiên (MSG hoặc FILE) quyết định loại stream. Với FILE, phần byte
        # còn lại đi thẳng qua `_relay`. Trả về False để giữ flow-control credit (back-pressure), None để tự cấp.
        st = s.streams.get(sid)
        if st is None:
            if len(s.streams) > 64:
                raise ProtocolError("too many open streams")
            st = s.streams[sid] = StreamState()
        hold = False
        if st.kind is None:
            st.buf.feed(data)
            hdr = st.buf.pop()
            if hdr is None:
                if fin:
                    raise ProtocolError("truncated message")
                return
            if hdr["t"] == "MSG":
                st.kind = "msg"
                self._route_msg(s, hdr)
            elif hdr["t"] == "FILE":
                st.kind = "file"
                self._start_file(s, st, hdr)
                rest = st.buf.take_all()
                if rest or fin:
                    hold = self._relay(s, st, sid, rest, fin, len(data))
            else:
                raise ProtocolError(f"unexpected stream message {hdr['t']}")
        elif st.kind == "file":
            hold = self._relay(s, st, sid, data, fin, len(data))
        if fin:
            s.streams.pop(sid, None)
        return False if hold else None

    def _route_msg(self, s, hdr):
        # Văn bản bị cắt ở MAX_TEXT; id do client đặt (<=64 ký tự) chỉ dùng để client đối chiếu SENT/ERR.
        # "ts" là giờ của server -> mọi người cùng sắp xếp hội thoại theo một đồng hồ chung.
        # Giới hạn độ dài tên người nhận: `to` được echo lại trong ERR, nếu không cắt thì một client có thể
        # buộc server gửi ngược một thông điệp gần 1 MB cho chính nó (khuếch đại lưu lượng).
        to = str(hdr.get("to", "*"))[:64]
        mid = str(hdr.get("id", ""))[:64]
        out = {"t": "MSG", "id": mid, "from": s.user, "to": to, "text": str(hdr.get("text", ""))[:MAX_TEXT],
               "ts": time.time()}
        if to == "*":
            targets = [d for u, d in self.by_user.items() if u != s.user]
        elif to in self.by_user and to != s.user:
            targets = [self.by_user[to]]
        else:
            self._send_ctrl(s, {"t": "ERR", "ref": mid, "msg": f"user '{to}' is not online"})
            return
        delivered = sum(1 for d in targets if self._deliver(d, out))
        if delivered == 0 and to != "*":              # người nhận vừa rớt mạng: báo lỗi chứ không báo "đã gửi"
            self._send_ctrl(s, {"t": "ERR", "ref": mid, "msg": f"user '{to}' is not online"})
            return
        self._send_ctrl(s, {"t": "SENT", "ref": mid, "ts": out["ts"], "n": delivered})

    def _start_file(self, s, st, hdr):
        fid, to = str(hdr.get("id", ""))[:64], str(hdr.get("to", ""))[:64]
        try:
            size = int(hdr.get("size", -1))
        except (TypeError, ValueError):
            size = -1
        dest = self.by_user.get(to)
        err = None
        if size < 0 or size > self.max_file:
            err = f"invalid or too large file (limit {self.max_file // 2**20} MB)"
        elif dest is None or dest.conn.closed or to == s.user:
            err = f"user '{to}' is not online"
        if err:
            self._send_ctrl(s, {"t": "ERR", "ref": fid, "msg": err})
            return                                    # st.relay stays None: body is discarded
        dsid = dest.conn.open_stream(1)               # lower priority than chat
        dest.conn.send(dsid, pack({"t": "FILE", "id": fid, "from": s.user, "name": safe_filename(hdr.get("name")),
                                   "size": size, "ts": time.time()}))
        st.relay = Relay(dest, dsid, size, fid)
        log.info("file relay %s -> %s: %s (%d bytes)", s.user, to, hdr.get("name"), size)

    def _relay(self, s, st, sid, data, fin, credit_len):
        """Cut-through relay with back-pressure. Returns True if flow-control credit must be held."""
        r = st.relay
        if r is None or r.dest.conn.closed:
            return False
        r.seen += len(data)
        if r.seen > r.size + 4096:
            self._send_ctrl(s, {"t": "ERR", "ref": r.fid, "msg": "file body larger than announced"})
            st.relay = None
            return False
        dc = r.dest.conn
        dc.send(r.dsid, data, fin)
        # Hold flow-control credit only while the receiver side is above the
        # relay watermark. Release as soon as it drops back under that mark,
        # not when the whole congestion window has drained to 64 KB.
        if not data or dc.buffered(r.dsid) < RELAY_HIGH:
            return False
        r.held += credit_len
        if not r.holding:
            r.holding = True
            src = s.conn

            def resume(src=src, sid=sid, relay=r):
                relay.holding = False
                n, relay.held = relay.held, 0
                if n and not src.closed:
                    src.consume(sid, n)

            dc.set_drain_callback(r.dsid, resume, below=RELAY_HIGH)
        return True


async def amain(args):
    loop = asyncio.get_running_loop()
    srv = Server(loop, args.host, args.port, args.data_dir, args.cc, args.sim_loss, args.sim_delay_ms / 1000,
                 args.max_file_mb, not args.no_beacon)
    print(f"CollabNet server on UDP port {srv.port} | congestion control: {args.cc}")
    print(f"Server key fingerprint (clients pin this on first use): {srv.fingerprint}")
    try:
        await asyncio.Event().wait()
    finally:
        srv.close()


def main():
    ap = argparse.ArgumentParser(description="CollabNet server")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=9000)
    ap.add_argument("--data-dir", default="./server_data")
    ap.add_argument("--cc", choices=["cubic", "bbr"], default="cubic")
    ap.add_argument("--max-file-mb", type=int, default=512)
    ap.add_argument("--no-beacon", action="store_true", help="disable LAN discovery broadcast")
    ap.add_argument("--sim-loss", type=float, default=0.0, help="simulated packet loss probability (testing)")
    ap.add_argument("--sim-delay-ms", type=float, default=0.0, help="simulated one-way delay (testing)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    loop = asyncio.SelectorEventLoop()               # selector loop works with add_reader on Windows too
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(amain(args))
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
