"""Test hồi quy cho các lỗi / tối ưu được sửa trong đợt rà soát mã nguồn.

Mỗi test tương ứng một vấn đề đã tái hiện được trên bản cũ:
  * B1  gửi tin cho peer vừa rớt kết nối làm server đóng nhầm kết nối của người gửi
  * B2  hai gói AUTH chồng nhau để lại user "ma" trong danh sách online
  * B3  tự kết nối lại bị server từ chối nhưng UI kẹt ở trạng thái "reconnecting"
  * P1  `Connection._packets_in_ranges` (thay cho vòng quét O(sent x ranges))
  * P2  BBR dùng bộ lọc max theo cửa sổ (deque đơn điệu) thay cho max() trên mọi mẫu
  * M1  `finished_recv` không phình theo số stream
  * D1  ghi file nguyên tử; D2 thông điệp đăng nhập; D3 tên file Windows; G1 Content-Length sai
"""
import asyncio
import os
import random
import sys
import tempfile
import unittest
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.core import AuthRejected, ClientCore
from client.gateway import Gateway
from common.congestion import Bbr, RateSample
from common.fsutil import atomic_write_json, atomic_write_text
from common.protocol import ProtocolError, pack, safe_filename
from server.server import Server, UserStore
from tests.test_gateway import X, http
from tests.test_transport import Pair


class ServerFixture(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.mkdtemp()
        self.server = Server(asyncio.get_running_loop(), "127.0.0.1", 0, os.path.join(self.tmp, "srv"), beacon=False)
        self.cores = []

    async def asyncTearDown(self):
        for c in self.cores:
            await c.logout()
        self.server.close()

    async def login(self, name, pw="secret"):
        c = ClientCore(asyncio.get_running_loop(), os.path.join(self.tmp, name))
        self.cores.append(c)
        await c.login("127.0.0.1", self.server.port, name, pw)
        return c


class ServerRobustnessTests(ServerFixture):
    async def test_b1_message_to_just_closed_peer_does_not_kick_sender(self):
        await self.login("alice")
        await self.login("bob")
        sa, sb = self.server.by_user["alice"], self.server.by_user["bob"]
        sb.conn._terminate("simulated idle timeout")     # closed=True nhưng on_close mới chỉ được lên lịch
        self.server._on_data(sa, 2, pack({"t": "MSG", "id": "m1", "to": "bob", "text": "hi"}), True)
        self.assertFalse(sa.conn.closed, "người gửi không được bị đóng kết nối")

    async def test_b1_broadcast_skips_closed_peer(self):
        await self.login("alice")
        await self.login("bob")
        await self.login("carol")
        sa = self.server.by_user["alice"]
        self.server.by_user["bob"].conn._terminate("gone")
        self.server._on_data(sa, 2, pack({"t": "MSG", "id": "m2", "to": "*", "text": "hello"}), True)
        self.assertFalse(sa.conn.closed)

    async def test_b2_overlapping_auth_is_rejected_and_leaves_no_ghost(self):
        from common.transport import Endpoint
        ep = Endpoint(asyncio.get_running_loop(), ("127.0.0.1", 0))
        conn = await ep.connect(("127.0.0.1", self.server.port))
        sid = conn.open_stream(0)
        conn.send(sid, pack({"t": "AUTH", "user": "userA", "pass": "secret"})
                  + pack({"t": "AUTH", "user": "userB", "pass": "secret"}))
        await asyncio.sleep(0.8)
        conn.close(0, "bye")
        await asyncio.sleep(0.6)
        ep.close()
        self.assertEqual(self.server.by_user, {}, "không được còn user 'ma' sau khi kết nối đóng")

    async def test_peers_report_current_address(self):
        await self.login("alice")
        s = self.server.by_user["alice"]
        s.conn.peer_addr = ("10.1.2.3", 4242)           # mô phỏng client đổi địa chỉ (NAT rebinding)
        p = self.server._peers()[0]
        self.assertEqual((p["ip"], p["port"]), ("10.1.2.3", 4242))


class ReconnectTests(ServerFixture):
    async def test_b3_rejected_relogin_goes_offline_and_stops_retrying(self):
        a = await self.login("alice")
        events = a.subscribe()                                # nhận mọi sự kiện UI phát ra
        a.creds = a.creds[:3] + ("WRONG-PASSWORD",)
        self.server.by_user["alice"].conn.close(9, "kick")
        end = asyncio.get_running_loop().time() + 8
        while a._want_online and asyncio.get_running_loop().time() < end:
            await asyncio.sleep(0.1)
        self.assertFalse(a._want_online)
        self.assertEqual((a.status, a.user), ("offline", None))
        emitted = []
        while not events.empty():
            emitted.append(events.get_nowait())
        self.assertIn(("status", "offline"), [(t, d.get("status")) for t, d in emitted][-3:],
                      "UI phải nhận trạng thái offline cuối cùng")
        self.assertTrue(a._reconnect_task.done())

    async def test_teardown_keeps_want_online_but_disconnect_clears_it(self):
        a = await self.login("alice")
        self.assertTrue(a._want_online)
        await a._teardown(announce=False)
        self.assertTrue(a._want_online, "lỗi xác thực tạm thời không được tắt tự kết nối lại")
        a._want_online = True
        await a._disconnect(announce=False)
        self.assertFalse(a._want_online)

    async def test_auth_rejected_is_an_auth_error(self):
        from client.core import AuthError
        self.assertTrue(issubclass(AuthRejected, AuthError))


class UserStoreTests(unittest.TestCase):
    def test_register_login_and_messages(self):
        path = os.path.join(tempfile.mkdtemp(), "users.json")
        st = UserStore(path)
        self.assertEqual(st.check_or_register("bob", "pw12"), (True, "registered"))
        self.assertEqual(st.check_or_register("bob", "pw12"), (True, "welcome back"))   # trước đây trả "wrong password"
        self.assertEqual(st.check_or_register("bob", "nope"), (False, "wrong password"))
        self.assertFalse(st.check_or_register("eve", "ab")[0])
        self.assertTrue(UserStore(path).check_or_register("bob", "pw12")[0], "phải được lưu xuống đĩa")

    def test_concurrent_registration_of_same_name_has_one_winner(self):
        import threading
        st = UserStore(os.path.join(tempfile.mkdtemp(), "users.json"))
        results = []
        ts = [threading.Thread(target=lambda p=p: results.append(st.check_or_register("same", p)))
              for p in ("pass-one", "pass-two", "pass-three", "pass-four")]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(sum(1 for ok, why in results if ok and why == "registered"), 1)


class FsUtilTests(unittest.TestCase):
    def test_atomic_write_replaces_and_leaves_no_temp_files(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "f.json")
        atomic_write_json(p, {"a": 1})
        atomic_write_json(p, {"a": 2})
        with open(p) as fh:
            self.assertEqual(fh.read(), '{"a": 2}')
        self.assertEqual(os.listdir(d), ["f.json"])

    def test_failed_write_keeps_old_content(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "f.txt")
        atomic_write_text(p, "old")
        with self.assertRaises(UnicodeEncodeError):
            atomic_write_text(p, "\ud800")                 # surrogate lẻ: không mã hoá được ra UTF-8
        with open(p) as fh:
            self.assertEqual(fh.read(), "old")
        self.assertEqual(os.listdir(d), ["f.txt"])


class ProtocolTests(unittest.TestCase):
    def test_windows_reserved_names(self):
        self.assertEqual(safe_filename("nul.txt"), "_nul.txt")
        self.assertEqual(safe_filename("CON"), "_CON")
        self.assertEqual(safe_filename("console.txt"), "console.txt")
        self.assertEqual(safe_filename("../../etc/passwd"), "passwd")
        self.assertEqual(safe_filename(".."), "file")

    def test_protocol_error_is_exception(self):
        self.assertTrue(issubclass(ProtocolError, Exception))


class TransportInternalsTests(unittest.IsolatedAsyncioTestCase):
    async def test_packets_in_ranges_matches_bruteforce(self):
        p = await Pair().start()
        try:
            conn, rnd = p.client, random.Random(7)
            conn.sent = {pn: object() for pn in rnd.sample(range(0, 400), 120)}
            for _ in range(300):
                ranges = []
                for _ in range(rnd.randint(1, 6)):
                    s = rnd.randint(0, 420)
                    ranges.append((s, s + rnd.choice([0, 1, 5, 40, 500, 2 ** 62])))   # gồm cả khoảng chồng lấn / khổng lồ
                expect = {pn for pn in conn.sent if any(s <= pn <= e for s, e in ranges)}
                got = conn._packets_in_ranges(ranges)
                self.assertEqual(len(got), len(set(map(id, got))), "mỗi gói chỉ xuất hiện một lần")
                self.assertEqual({pn for pn, o in conn.sent.items() if any(o is g for g in got)}, expect)
        finally:
            p.close()

    async def test_finished_recv_stays_compact(self):
        p = await Pair().start()
        try:
            sids = [p.client.open_stream(0) for _ in range(60)]
            for sid in sids:
                p.client.send(sid, b"x" * 100, fin=True)
            for sid in sids:
                await p.wait_fin(sid, 10)
            srv = p.server_conns[0]
            self.assertLessEqual(len(srv.finished_recv.r), 2)
            self.assertTrue(all(srv.finished_recv.contains(sid >> 1) for sid in sids))
        finally:
            p.close()


class BbrWindowedMaxTests(unittest.TestCase):
    def test_matches_bruteforce_window_max(self):
        rnd = random.Random(3)
        bbr, shadow = Bbr(), deque()                        # shadow: cách tính cũ (giữ mọi mẫu, max() mỗi lần)
        delivered = 0
        for i in range(4000):
            delivered += 1200
            rate = rnd.choice([0, rnd.uniform(1e5, 5e6)])
            app_limited = rnd.random() < 0.3
            sample = RateSample(rate, max(0, delivered - rnd.randint(1200, 60000)), app_limited)
            before_bw = bbr.btl_bw
            bbr.on_ack(i * 0.001, 1200, i * 0.001 - 0.02, 0.02, sample, 20000, 0.02)
            if sample.rate > 0 and (not sample.app_limited or sample.rate >= before_bw):
                shadow.append((bbr.round, sample.rate))
            while shadow and shadow[0][0] < bbr.round - Bbr.BW_WINDOW:
                shadow.popleft()
            self.assertEqual(bbr.btl_bw, max((r for _, r in shadow), default=0.0), f"lệch ở bước {i}")


class GatewayHardeningTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.mkdtemp()
        self.core = ClientCore(asyncio.get_running_loop(), self.tmp + "/c")
        self.gw = Gateway(self.core, "127.0.0.1", 0, "127.0.0.1:1")
        await self.gw.start()

    async def asyncTearDown(self):
        self.gw.close()

    async def test_bad_content_length_is_400_not_500(self):
        for value in ("abc", "-5"):
            s, _, body = await http(self.gw.port, "POST", "/api/send", {**X, "Content-Length": value})
            self.assertEqual(s, 400, (value, body))

    async def test_negative_upload_size_is_400(self):
        h = {**X, "x-to": "bob", "Content-Length": "-1"}
        s, _, _ = await http(self.gw.port, "POST", "/api/upload", h)
        self.assertEqual(s, 400)


if __name__ == "__main__":
    unittest.main()
