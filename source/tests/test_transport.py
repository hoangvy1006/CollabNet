"""Transport tests: crypto, ranges, reliable streams under loss/delay, HoL-blocking, CC algorithms.

Kiểm thử tầng transport bằng cách ghép hai Endpoint thật trên loopback (không mock), nên bao gồm cả
mã hoá, ACK/SACK, gửi lại và điều khiển tắc nghẽn chạy đúng như khi triển khai.
"""
import asyncio
import hashlib
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import crypto
from common.packet import decode_frames, enc_ack, enc_close, enc_max_stream_data, enc_ping, enc_stream
from common.rangeset import RangeSet
from common.transport import Endpoint


class UnitTests(unittest.TestCase):
    def test_rangeset(self):
        r = RangeSet()
        r.add(0, 5); r.add(10, 15); r.add(5, 10)
        self.assertEqual(r.r, [(0, 15)])
        r.add(20, 25)
        self.assertEqual(r.missing(0, 30), [(15, 20), (25, 30)])
        self.assertEqual(r.contiguous_end(0), 15)
        self.assertTrue(r.contains(22) and not r.contains(17))

    def test_frames_roundtrip(self):
        buf = (enc_ack([(10, 12), (3, 5)], 77) + enc_stream(4, 1000, b"hello", True) + enc_ping()
               + enc_max_stream_data(5, 99999) + enc_close(3, "bye"))
        f = decode_frames(buf)
        self.assertEqual(f[0], ("A", [(10, 12), (3, 5)], 77))
        self.assertEqual(f[1], ("S", 4, 1000, b"hello", True))
        self.assertEqual(f[2], ("P",))
        self.assertEqual(f[3], ("M", 5, 99999))
        self.assertEqual(f[4], ("C", 3, "bye"))
        with self.assertRaises(ValueError):
            decode_frames(b"\xff\x00")
        # Frame CLOSE khai báo độ dài lý do (4096) lớn hơn số byte còn lại: phải bị coi là hỏng thay vì
        # âm thầm trả về lý do rỗng (lỗi cũ).
        with self.assertRaises(ValueError):
            decode_frames(b"\x07\x00\x01\x10\x00")

    def test_crypto(self):
        a_priv, a_pub = crypto.new_ephemeral()
        b_priv, b_pub = crypto.new_ephemeral()
        k1 = crypto.derive_keys(a_priv, b_pub, a_pub, b_pub)
        k2 = crypto.derive_keys(b_priv, a_pub, a_pub, b_pub)
        self.assertEqual(k1, k2)
        c = crypto.PacketCipher(k1[0])
        ct = c.seal(7, b"hdr", b"secret")
        self.assertEqual(c.open(7, b"hdr", ct), b"secret")
        with self.assertRaises(Exception):
            c.open(8, b"hdr", ct)           # wrong packet number -> wrong nonce
        with self.assertRaises(Exception):
            c.open(7, b"HDR", ct)           # header tampering detected
        stored = crypto.hash_password("pw", iterations=1000)
        self.assertTrue(crypto.verify_password("pw", stored))
        self.assertFalse(crypto.verify_password("pw2", stored))


class Pair:
    """A connected client/server pair over loopback with optional simulated loss/delay."""

    def __init__(self, cc="cubic", loss=0.0, delay=0.0, jitter=0.0):
        self.cc, self.loss, self.delay, self.jitter = cc, loss, delay, jitter
        self.server_conns, self.rx = [], {}

    async def start(self):
        loop = asyncio.get_running_loop()
        key = crypto.load_or_create_identity(os.path.join(tempfile.mkdtemp(), "id.key"))
        self.sep = Endpoint(loop, ("127.0.0.1", 0), identity=key, cc=self.cc, sim_loss=self.loss,
                            sim_delay=self.delay, sim_jitter=self.jitter)
        self.sep.on_accept = self._accept
        self.cep = Endpoint(loop, ("127.0.0.1", 0), cc=self.cc, sim_loss=self.loss, sim_delay=self.delay,
                            sim_jitter=self.jitter)
        self.client = await self.cep.connect(self.sep.addr)
        for _ in range(100):
            if self.server_conns:
                break
            await asyncio.sleep(0.01)
        return self

    def _accept(self, conn):
        self.server_conns.append(conn)
        conn.on_stream_data = lambda c, sid, data, fin: self._on_data(sid, data, fin)

    def _on_data(self, sid, data, fin):
        st = self.rx.setdefault(sid, {"buf": bytearray(), "fin": False, "t": None})
        st["buf"] += data
        if fin:
            st["fin"], st["t"] = True, time.monotonic()

    async def wait_fin(self, sid, timeout=60):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if self.rx.get(sid, {}).get("fin"):
                return self.rx[sid]
            await asyncio.sleep(0.01)
        raise TimeoutError(f"stream {sid} not finished; got {len(self.rx.get(sid, {}).get('buf', b''))} bytes")

    def close(self):
        self.cep.close()
        self.sep.close()


class TransportTests(unittest.IsolatedAsyncioTestCase):
    async def _bulk(self, cc, loss, delay, size, jitter=0.0):
        p = await Pair(cc, loss, delay, jitter).start()
        try:
            data = os.urandom(size)
            sid = p.client.open_stream(1)
            t0 = time.monotonic()
            p.client.send(sid, data, fin=True)
            st = await p.wait_fin(sid)
            dt = time.monotonic() - t0
            self.assertEqual(hashlib.sha256(bytes(st["buf"])).digest(), hashlib.sha256(data).digest())
            self.assertTrue(await asyncio.wait_for(p.client.send_done(sid), 30))
            return dt, p.client.stats()
        finally:
            p.close()

    async def test_clean_link_cubic(self):
        dt, s = await self._bulk("cubic", 0.0, 0.0, 4_000_000)
        print(f"\n  cubic clean 4MB: {dt:.2f}s", s)

    async def test_lossy_cubic(self):
        dt, s = await self._bulk("cubic", 0.05, 0.01, 2_000_000, 0.004)
        print(f"\n  cubic 5% loss + reordering: {dt:.2f}s", s)
        self.assertGreater(s["lost_pkts"], 0)

    async def test_lossy_bbr(self):
        dt, s = await self._bulk("bbr", 0.05, 0.01, 2_000_000, 0.004)
        print(f"\n  bbr 5% loss + reordering: {dt:.2f}s", s)

    async def test_no_hol_blocking(self):
        """A tiny message on its own stream must arrive quickly while a big file saturates the link."""
        p = await Pair("cubic", 0.03, 0.02).start()
        try:
            big = p.client.open_stream(1)
            p.client.send(big, os.urandom(3_000_000), fin=True)
            await asyncio.sleep(0.3)                       # let the file transfer get going
            lat = []
            for i in range(5):
                sid = p.client.open_stream(0)
                t0 = time.monotonic()
                p.client.send(sid, b"ping %d" % i, fin=True)
                st = await p.wait_fin(sid, 10)
                lat.append(st["t"] - t0)
                self.assertEqual(bytes(st["buf"]), b"ping %d" % i)
                await asyncio.sleep(0.05)
            await p.wait_fin(big)
            print("\n  chat latency while file in flight (ms):", [round(x * 1000) for x in lat])
            self.assertLess(max(lat), 1.5)                 # far less than file transfer time
        finally:
            p.close()

    async def test_flow_control_backpressure(self):
        """Receiver that withholds credit stops the sender at the window size."""
        p = await Pair().start()
        try:
            p.server_conns[0].on_stream_data = lambda c, sid, data, fin: False   # never consume
            sid = p.client.open_stream()
            p.client.send(sid, os.urandom(2_000_000), fin=True)
            await asyncio.sleep(1.0)
            got = p.client.acked_offset(sid)
            self.assertLessEqual(got, 512 * 1024)
            self.assertGreater(got, 0)
        finally:
            p.close()

    async def test_untrusted_server_rejected(self):
        loop = asyncio.get_running_loop()
        key = crypto.load_or_create_identity(os.path.join(tempfile.mkdtemp(), "id.key"))
        sep = Endpoint(loop, ("127.0.0.1", 0), identity=key)
        cep = Endpoint(loop)
        def verify(pub):
            raise ConnectionError("pinned key mismatch")
        try:
            with self.assertRaises(ConnectionError):
                await cep.connect(sep.addr, verify=verify, timeout=3)
        finally:
            cep.close(); sep.close()

    async def test_disconnect_detected(self):
        p = await Pair().start()
        closed = asyncio.Event()
        p.server_conns[0].on_close = lambda c, r: closed.set()
        p.client.close(0, "bye")
        await asyncio.wait_for(closed.wait(), 3)
        p.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
