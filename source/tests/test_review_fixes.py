"""Kiểm thử hồi quy cho các lỗi tìm thấy khi review codebase (dựa trên knowledge graph).

1. Kết nối P2P đứt giữa lúc nhận file: bên nhận phải đóng file, xoá `.part` và báo lỗi (trước đây treo "active").
2. Người nhận đầu tiên trong chat chung không kết nối P2P được: những người khác vẫn phải nhận được file.
3. Mẫu tốc độ giao hàng (BBR) phải dùng cả thời gian giữa hai lần ACK (ack_elapsed), không chỉ send_elapsed.
4. `fid` do trình duyệt gửi lên (X-File-Id) không được dùng làm đường dẫn thoát khỏi thư mục outbox.
"""
import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.discovery import Beacon, discover
from common.transport import Connection, Endpoint, SentPacket
from tests import test_e2e as _e2e
from tests.test_e2e import chunked


class ReviewFixTests(_e2e.E2E):
    # Không chạy lại các test kế thừa từ E2E (đã chạy trong test_e2e.py).
    test_full_scenario = test_auth_errors = test_auto_reconnect = test_relogin_kicks_old_session = None

    async def test_p2p_drop_mid_transfer_cleans_receiver(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        await ca.wait("peers", lambda d: len(d["peers"]) == 2)
        gate = asyncio.Event()

        async def slow():
            yield os.urandom(100_000)
            await gate.wait()                       # treo giữa chừng như người gửi bị treo / mất mạng
            yield b""

        task = asyncio.ensure_future(alice.send_file("bob", "drop.bin", 400_000, slow()))
        await cb.wait("file_start")
        await cb.wait("file_progress", lambda d: d["done"] > 0)
        conn, _fp = alice._p2p_conns["bob"]
        conn.close(0, "simulated crash")            # kết nối P2P đứt
        err = await cb.wait("error", timeout=10)
        self.assertIn("drop.bin", err["text"])
        self.assertEqual([n for n in os.listdir(bob.download_dir) if n.endswith(".part")], [])
        self.assertEqual(bob.files[-1]["status"], "failed")
        self.assertEqual(bob._p2p_rx, {})
        task.cancel()
        try:
            await task
        except BaseException:
            pass

    async def test_group_file_reaches_others_when_first_peer_unreachable(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        carol, cc_ = await self.client("carol")
        await ca.wait("peers", lambda d: len(d["peers"]) == 3)
        bob._p2p_ep.close()                          # bob còn online với server nhưng cổng P2P đã chết
        data = os.urandom(30_000)
        await alice.send_file("*", "group.bin", len(data), chunked(data))
        got = await cc_.wait("file_received", lambda d: d["name"] == "group.bin", timeout=20)
        self.assertEqual(got["size"], len(data))
        self.assertEqual(alice.files[-1]["status"], "done")

    async def test_bad_file_id_is_rejected(self):
        alice, _ = await self.client("alice")
        bob, _ = await self.client("bob")
        with self.assertRaises(ValueError):
            await alice.send_file("bob", "x.bin", 3, chunked(b"abc"), fid="../../escape")
        self.assertFalse(os.path.exists(os.path.join(alice.state_dir, "..", "escape.bin")))


class RateSampleTests(unittest.IsolatedAsyncioTestCase):

    async def test_rate_sample_uses_ack_elapsed(self):
        loop = asyncio.get_running_loop()
        ep = Endpoint(loop, ("127.0.0.1", 0))
        try:
            conn = Connection(ep, True, ("127.0.0.1", 9), 1, 2, b"k" * 32, b"k" * 32, "bbr")
            now = loop.time()
            conn.delivered, conn.delivered_time = 10_000, now
            p = SentPacket()
            p.pn, p.time, p.size, p.frames = 0, now - 0.01, 1000, []
            p.delivered, p.delivered_time, p.first_sent, p.app_limited = 0, now - 1.0, now - 0.01, False
            conn.sent[0], conn.bytes_in_flight, conn.next_pn = p, 1000, 1
            seen = []
            conn.cc.on_ack = lambda *a: seen.append(a[4])
            conn._on_packet_acked(p, now, None)
            # 11 000 byte giao trong 1 giây giữa hai lần ACK -> ~11 kB/s, không phải hàng tỉ byte/s
            self.assertAlmostEqual(seen[0].rate, 11_000, delta=200)
            conn._terminate("test done")
        finally:
            ep.close()


class DiscoveryTests(unittest.IsolatedAsyncioTestCase):

    async def test_discover_finds_local_beacon(self):
        # Trước đây discover() ném AttributeError trên Python 3.10 (loop.sock_recvfrom chỉ có từ 3.11).
        beacon = Beacon(asyncio.get_running_loop(), 12345, "test-server", interval=0.2)
        try:
            found = await discover(1.0)
        finally:
            beacon.close()
        self.assertIn({"host": "127.0.0.1", "port": 12345, "name": "test-server"}, found)


if __name__ == "__main__":
    unittest.main(verbosity=2)
