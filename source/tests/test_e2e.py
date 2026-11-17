"""Kiểm thử end-to-end: server thật + nhiều ClientCore trên UDP loopback (có thể mô phỏng mạng xấu)."""
import asyncio
import hashlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.core import AuthError, ClientCore
from server.server import Server


async def chunked(data, n=40000):
    for i in range(0, len(data), n):
        yield data[i:i + n]
        await asyncio.sleep(0)


class Collector:
    """Thu sự kiện từ ClientCore và chờ một sự kiện khớp điều kiện (có timeout)."""

    def __init__(self, core):
        self.q, self.events = core.subscribe(), []

    async def wait(self, typ, pred=lambda d: True, timeout=30):
        async def go():
            while True:
                for i, (t, d) in enumerate(self.events):
                    if t == typ and pred(d):
                        del self.events[i]
                        return d
                self.events.append(await self.q.get())
        return await asyncio.wait_for(go(), timeout)


class E2E(unittest.IsolatedAsyncioTestCase):
    """Bộ khung kiểm thử end-to-end dùng chung: dựng server + client trong thư mục tạm."""

    loss, delay, cc = 0.0, 0.0, "cubic"

    async def asyncSetUp(self):
        self.tmp = tempfile.mkdtemp()
        loop = asyncio.get_running_loop()
        self.server = Server(loop, "127.0.0.1", 0, os.path.join(self.tmp, "srv"), self.cc, self.loss, self.delay,
                             beacon=False)
        self.clients = []

    async def asyncTearDown(self):
        for c in self.clients:
            await c.logout()
        self.server.close()

    async def client(self, name, pw="secret", host_port=None):
        c = ClientCore(asyncio.get_running_loop(), os.path.join(self.tmp, name), self.cc, self.loss, self.delay)
        self.clients.append(c)
        col = Collector(c)
        await c.login("127.0.0.1", host_port or self.server.port, name, pw)
        return c, col

    async def test_full_scenario(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        carol, cc_ = await self.client("carol")
        # presence: mọi người thấy 3 user kèm ip/port
        d = await ca.wait("peers", lambda d: len(d["peers"]) == 3)
        self.assertTrue(all(p["ip"] == "127.0.0.1" and p["port"] > 0 for p in d["peers"]))
        # tin chung (broadcast)
        alice.send_message("*", "hello everyone")
        m = await cb.wait("msg"); self.assertEqual((m["from"], m["text"], m["to"]), ("alice", "hello everyone", "*"))
        await cc_.wait("msg")
        # tin riêng không được lọt tới carol
        bob.send_message("alice", "psst")
        m = await ca.wait("msg", lambda d: not d["mine"]); self.assertEqual(m["text"], "psst")
        await asyncio.sleep(0.3)
        while not cc_.q.empty():
            cc_.events.append(cc_.q.get_nowait())
        self.assertFalse([e for e in cc_.events if e[0] == "msg" and e[1]["text"] == "psst"])
        # người nhận offline -> báo lỗi
        alice.send_message("nobody", "x")
        e = await ca.wait("error"); self.assertIn("not online", e["text"])
        # truyền file P2P (3 MB ngẫu nhiên) alice -> bob, kiểm SHA-256
        data = os.urandom(3_000_000)
        await alice.send_file("bob", "data.bin", len(data), chunked(data))
        r = await cb.wait("file_received")
        with open(os.path.join(bob.download_dir, r["name"]), "rb") as fh:
            got = fh.read()
        self.assertEqual(hashlib.sha256(got).digest(), hashlib.sha256(data).digest())
        # file rỗng
        await bob.send_file("alice", "empty.txt", 0, chunked(b""))
        r = await ca.wait("file_received"); self.assertEqual(r["size"], 0)
        # ngắt đột ngột (không gửi BYE): carol biến mất, những người khác được báo ngay
        carol.conn.close(0, "x")
        d = await ca.wait("peers", lambda d: len(d["peers"]) == 2, timeout=5)
        self.assertEqual(sorted(p["user"] for p in d["peers"]), ["alice", "bob"])

    async def test_auth_errors(self):
        await self.client("dave", "goodpass")
        with self.assertRaises(AuthError):
            await self.client("dave", "WRONG")
        with self.assertRaises(AuthError):
            await self.client("x", "pw")                  # tên không hợp lệ (quá ngắn)
        # server không tới được: hết giờ bắt tay thay vì treo mãi
        with self.assertRaises(ConnectionError):
            from common.transport import Endpoint
            ep = Endpoint(asyncio.get_running_loop())
            try:
                await ep.connect(("127.0.0.1", 9), timeout=1.0)
            finally:
                ep.close()

    async def test_relogin_kicks_old_session(self):
        a1, c1 = await self.client("erin")
        a2, c2 = await self.client("erin")
        e = await c1.wait("status", lambda d: d["status"] == "offline", timeout=5)
        self.assertIn("another place", e["reason"])
        self.assertEqual(a2.status, "online")

    async def test_auto_reconnect(self):
        a, ca = await self.client("frank")
        b, cb = await self.client("gina")
        b.conn.close(0, "network glitch")                 # mô phỏng mất kết nối (client vẫn muốn online)
        await cb.wait("status", lambda d: d["status"] == "reconnecting", timeout=5)
        await cb.wait("notice", lambda d: "Reconnected" in d["text"], timeout=15)
        self.assertEqual(b.status, "online")


class E2ELossy(E2E):
    """Cùng kịch bản trên link mất 4% gói và trễ 15 ms một chiều, dùng BBR."""
    loss, delay, cc = 0.04, 0.015, "bbr"

    async def test_auth_errors(self):
        pass                                              # đã được kiểm ở biến thể link sạch


if __name__ == "__main__":
    unittest.main(verbosity=2)
