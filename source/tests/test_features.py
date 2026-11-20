"""Kiểm thử các tính năng chat/file mà người dùng thấy được: trạng thái gửi, sắp xếp theo giờ server,
upload bị ngắt giữa chừng, giới hạn kích thước file, xem trước ảnh và lịch sử sau khi đăng xuất.
"""
import hashlib
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.test_e2e import E2E, chunked


class FeatureTests(E2E):
    """Kiểm thử những tính năng người dùng thấy được, chạy trên bộ khung E2E."""

    async def test_message_status_and_history(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        mid = alice.send_message("bob", "xin chào")
        self.assertEqual(alice.history[-1]["status"], "pending")
        sent = await ca.wait("sent", lambda d: d["ref"] == mid)
        self.assertEqual(alice.history[-1]["status"], "sent")
        self.assertEqual(alice.history[-1]["ts"], sent["ts"])            # giờ server trở thành mốc chung
        await cb.wait("msg")
        self.assertEqual(bob.history[-1]["from"], "alice")
        # broadcast không còn ai nghe thì báo n == 0
        await bob.logout()
        mid2 = alice.send_message("*", "có ai không?")
        self.assertEqual((await ca.wait("sent", lambda d: d["ref"] == mid2))["n"], 0)
        # tin riêng gửi khi bob đã đăng xuất vẫn được server lưu (n = 0 người đang online)
        mid3 = alice.send_message("bob", "bob ơi")
        offline = await ca.wait("sent", lambda d: d["ref"] == mid3)
        self.assertEqual(offline["n"], 0)
        kept = [m for m in alice.snapshot()["history"] if m["id"] == mid3][0]
        self.assertEqual(kept["status"], "sent")

    async def test_file_items_and_limit_announced(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        self.assertEqual(alice.max_file, 512 * 1024 * 1024)
        data = os.urandom(300_000)
        await alice.send_file("bob", "a.bin", len(data), chunked(data))
        r = await cb.wait("file_received")
        f_up = [f for f in alice.snapshot()["files"] if f["id"] == r["id"]][0]
        f_dn = [f for f in bob.snapshot()["files"] if f["id"] == r["id"]][0]
        self.assertEqual((f_up["status"], f_up["mine"], f_up["to"]), ("done", True, "bob"))
        self.assertEqual((f_dn["status"], f_dn["mine"], f_dn["to"]), ("done", False, "bob"))

    async def test_chat_history_restored_after_logout(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        alice.send_message("bob", "trước khi tắt máy")
        await cb.wait("msg", lambda d: d["text"] == "trước khi tắt máy")
        bob.send_message("alice", "tin trả lời")
        await ca.wait("msg", lambda d: d["text"] == "tin trả lời")
        await alice.logout()
        self.assertEqual(alice.history, [])           # client không giữ lịch sử giữa các phiên
        await alice.login("127.0.0.1", self.server.port, "alice", "secret")
        hist = await ca.wait("history", lambda d: d["items"])      # bỏ qua sự kiện rỗng của lần đăng nhập đầu
        mine = {m["text"]: m["mine"] for m in hist["items"]}
        self.assertTrue(mine["trước khi tắt máy"])
        self.assertFalse(mine["tin trả lời"])
        self.assertEqual([m["text"] for m in alice.history], ["trước khi tắt máy", "tin trả lời"])

    async def test_new_account_does_not_see_older_broadcasts(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        alice.send_message("*", "tin chung trước khi carol tồn tại")
        await cb.wait("msg", lambda d: d["text"] == "tin chung trước khi carol tồn tại")
        carol, cc_ = await self.client("carol")            # tài khoản mới đăng ký ở đây
        hist = await cc_.wait("history")
        self.assertEqual(hist["items"], [])                # không thấy tin chung cũ hơn thời điểm tạo tài khoản
        alice.send_message("*", "tin chung sau khi carol vào")
        await cc_.wait("msg", lambda d: d["text"] == "tin chung sau khi carol vào")
        await carol.logout()
        await carol.login("127.0.0.1", self.server.port, "carol", "secret")
        texts = [m["text"] for m in (await cc_.wait("history"))["items"]]
        self.assertIn("tin chung sau khi carol vào", texts)
        self.assertNotIn("tin chung trước khi carol tồn tại", texts)

    async def test_group_file_and_offline_delivery(self):
        """Chat chung nhận file; người offline vẫn nhận tin và file (nhóm + riêng) khi đăng nhập lại."""
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        carol, cc_ = await self.client("carol")
        await bob.logout()
        alice.send_message("bob", "riêng khi vắng")
        await ca.wait("sent", lambda d: d["n"] == 0)
        alice.send_message("*", "nhóm khi bob vắng")
        await cc_.wait("msg", lambda d: d["text"] == "nhóm khi bob vắng")
        private = os.urandom(50_000)
        await alice.send_file("bob", "rieng.bin", len(private), chunked(private))
        queued = await ca.wait("file_queued")
        self.assertEqual(queued["to"], "bob")
        group = os.urandom(40_000)
        await alice.send_file("*", "nhom.bin", len(group), chunked(group))
        got_carol = await cc_.wait("file_received", lambda d: d["name"].startswith("nhom"))
        self.assertEqual(got_carol["size"], len(group))
        carol_item = [f for f in carol.files if f["id"] == got_carol["id"]][0]
        self.assertEqual(carol_item["to"], "*")
        with open(os.path.join(carol.download_dir, got_carol["name"]), "rb") as fh:
            self.assertEqual(hashlib.sha256(fh.read()).digest(), hashlib.sha256(group).digest())
        await bob.login("127.0.0.1", self.server.port, "bob", "secret")
        hist = await cb.wait("history", lambda d: d["items"])
        texts = [m.get("text") for m in hist["items"]]
        self.assertIn("riêng khi vắng", texts)
        self.assertIn("nhóm khi bob vắng", texts)
        cards = {m["name"]: m for m in hist["items"] if m.get("kind") == "file"}
        self.assertEqual(cards["rieng.bin"]["to"], "bob")
        self.assertEqual(cards["nhom.bin"]["to"], "*")
        got_private = await cb.wait("file_received", lambda d: d["name"].startswith("rieng"))
        got_group = await cb.wait("file_received", lambda d: d["name"].startswith("nhom"))
        for rec, raw in ((got_private, private), (got_group, group)):
            with open(os.path.join(bob.download_dir, rec["name"]), "rb") as fh:
                self.assertEqual(hashlib.sha256(fh.read()).digest(), hashlib.sha256(raw).digest())
        self.assertEqual([f for f in bob.files if f["id"] == got_group["id"]][0]["to"], "*")

    async def test_interrupted_upload_does_not_leave_receiver_hanging(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")

        async def broken():
            yield os.urandom(100_000)
            raise ConnectionError("upload interrupted")
        with self.assertRaises(ConnectionError):
            await alice.send_file("bob", "half.bin", 500_000, broken())
        err = await cb.wait("error")
        self.assertIn("incomplete", err["text"])
        self.assertEqual([n for n in os.listdir(bob.download_dir)], [])      # không còn file .part rác
        self.assertEqual(alice.files[-1]["status"], "failed")
        self.assertEqual(bob.files[-1]["status"], "failed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
