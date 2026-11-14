"""Tests for the chat/file upgrades: delivery status, server-clock ordering, aborted uploads, file limit, inline preview.

Kiểm thử các hành vi người dùng thấy được: trạng thái "đang gửi/đã gửi/lỗi", sắp xếp theo giờ server,
upload bị ngắt giữa chừng và giới hạn kích thước file do server công bố.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.test_e2e import E2E, chunked


class FeatureTests(E2E):
    async def test_message_status_and_history(self):
        alice, ca = await self.client("alice")
        bob, cb = await self.client("bob")
        mid = alice.send_message("bob", "xin chào")
        self.assertEqual(alice.history[-1]["status"], "pending")
        sent = await ca.wait("sent", lambda d: d["ref"] == mid)
        self.assertEqual(alice.history[-1]["status"], "sent")
        self.assertEqual(alice.history[-1]["ts"], sent["ts"])            # server clock becomes the shared timestamp
        await cb.wait("msg")
        self.assertEqual(bob.history[-1]["from"], "alice")
        # broadcast with nobody else listening reports n == 0
        await bob.logout()
        mid2 = alice.send_message("*", "có ai không?")
        self.assertEqual((await ca.wait("sent", lambda d: d["ref"] == mid2))["n"], 0)
        # message to an offline user is marked failed in the snapshot (survives a UI reload)
        mid3 = alice.send_message("bob", "bob ơi")
        await ca.wait("error", lambda d: d["ref"] == mid3)
        failed = [m for m in alice.snapshot()["history"] if m["id"] == mid3][0]
        self.assertEqual(failed["status"], "failed")

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
        self.assertEqual([n for n in os.listdir(bob.download_dir)], [])      # no stray .part file
        self.assertEqual(alice.files[-1]["status"], "failed")
        self.assertEqual(bob.files[-1]["status"], "failed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
