"""Bước 2 của đề: client kết nối TCP tới server và nhận ACK (HELLO -> HELLO_ACK) trước khi dùng UDP."""
import asyncio
import os
import socket
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.core import ClientCore
from common.protocol import MsgBuffer, pack
from server.server import Server


async def tcp_exchange(port, payload: bytes, timeout=5.0):
    """Gửi `payload` qua TCP thô tới server, trả về thông điệp đầu tiên nhận được (None nếu server đóng)."""
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        await loop.sock_connect(sock, ("127.0.0.1", port))
        await loop.sock_sendall(sock, payload)
        buf = MsgBuffer()

        async def read():
            while (m := buf.pop()) is None:
                data = await loop.sock_recv(sock, 4096)
                if not data:
                    return None
                buf.feed(data)
            return m
        return await asyncio.wait_for(read(), timeout)
    finally:
        sock.close()


class TcpHandshakeTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.tmp = tempfile.mkdtemp()
        self.server = Server(asyncio.get_running_loop(), "127.0.0.1", 0, os.path.join(self.tmp, "srv"), beacon=False)
        self.cores = []

    async def asyncTearDown(self):
        for c in self.cores:
            await c.logout()
        self.server.close()

    async def test_hello_gets_ack(self):
        ack = await tcp_exchange(self.server.port, pack({"t": "HELLO", "proto": 1, "user": "alice"}))
        self.assertEqual(ack["t"], "HELLO_ACK")
        self.assertEqual(ack["udp_port"], self.server.port)
        self.assertEqual(ack["fp"], self.server.fingerprint)

    async def test_wrong_version_and_garbage_do_not_hurt_server(self):
        fail = await tcp_exchange(self.server.port, pack({"t": "HELLO", "proto": 99}))
        self.assertEqual(fail["t"], "HELLO_FAIL")
        self.assertIsNone(await tcp_exchange(self.server.port, b"\x00\x00\x00\x05xxxxx"))   # JSON rác -> đóng
        self.assertIsNone(await tcp_exchange(self.server.port, b"\xff\xff\xff\xff"))         # độ dài khổng lồ -> đóng
        ack = await tcp_exchange(self.server.port, pack({"t": "HELLO", "proto": 1}))
        self.assertEqual(ack["t"], "HELLO_ACK")                                             # server vẫn phục vụ

    async def test_many_concurrent_tcp_handshakes(self):
        acks = await asyncio.gather(*(tcp_exchange(self.server.port, pack({"t": "HELLO", "proto": 1}))
                                      for _ in range(30)))
        self.assertTrue(all(a["t"] == "HELLO_ACK" for a in acks))

    async def test_client_login_does_tcp_handshake_first(self):
        c = ClientCore(asyncio.get_running_loop(), os.path.join(self.tmp, "alice"))
        self.cores.append(c)
        q = c.subscribe()
        await c.login("127.0.0.1", self.server.port, "alice", "secret")
        notices = []
        while not q.empty():
            t, d = q.get_nowait()
            if t == "notice":
                notices.append(d["text"])
        self.assertTrue(any("TCP handshake OK" in n for n in notices), notices)
        self.assertEqual(c.status, "online")

    async def test_no_tcp_listener_gives_clear_error(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        dead = s.getsockname()[1]
        s.close()                                   # cổng không có ai lắng nghe -> TCP bị từ chối ngay
        c = ClientCore(asyncio.get_running_loop(), os.path.join(self.tmp, "bob"))
        self.cores.append(c)
        with self.assertRaises(ConnectionError) as cm:
            await c.login("127.0.0.1", dead, "bob", "secret")
        self.assertIn("TCP", str(cm.exception))
        self.assertEqual(c.status, "offline")


if __name__ == "__main__":
    unittest.main(verbosity=2)
