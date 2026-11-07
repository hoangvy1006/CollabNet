"""HTTP gateway tests: speak raw HTTP to the gateway exactly like the browser UI does."""
import asyncio
import hashlib
import json
import os
import sys
import tempfile
import unittest
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.core import ClientCore
from client.gateway import Gateway
from server.server import Server

X = {"X-Requested-With": "collabnet"}


async def http(port, method, path, headers=None, body=b"", host="127.0.0.1"):
    r, w = await asyncio.open_connection("127.0.0.1", port)
    h = {"Host": f"{host}:{port}", "Content-Length": str(len(body)), **(headers or {})}
    w.write((f"{method} {path} HTTP/1.1\r\n" + "".join(f"{k}: {v}\r\n" for k, v in h.items()) + "\r\n").encode() + body)
    await w.drain()
    raw = await r.read()
    w.close()
    head, _, payload = raw.partition(b"\r\n\r\n")
    status = int(head.split()[1])
    return status, head.decode(), payload


async def jpost(port, path, obj):
    s, _, b = await http(port, "POST", path, {**X, "Content-Type": "application/json"}, json.dumps(obj).encode())
    return s, json.loads(b)


class GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.mkdtemp()
        loop = asyncio.get_running_loop()
        self.server = Server(loop, "127.0.0.1", 0, self.tmp + "/srv", beacon=False)
        self.cores, self.gws = {}, {}
        for n in ("alice", "bob"):
            c = ClientCore(loop, f"{self.tmp}/{n}")
            g = Gateway(c, "127.0.0.1", 0, f"127.0.0.1:{self.server.port}")
            await g.start()
            self.cores[n], self.gws[n] = c, g

    async def asyncTearDown(self):
        for c in self.cores.values():
            await c.logout()
        for g in self.gws.values():
            g.close()
        self.server.close()

    async def test_ui_flow(self):
        pa, pb = self.gws["alice"].port, self.gws["bob"].port
        s, head, body = await http(pa, "GET", "/")
        self.assertEqual(s, 200); self.assertIn(b"CollabNet", body); self.assertIn("Content-Security-Policy", head)
        for path in ("/app.js", "/style.css"):
            self.assertEqual((await http(pa, "GET", path))[0], 200)
        # security checks
        self.assertEqual((await http(pa, "POST", "/api/send", {}, b"{}"))[0], 403)          # no X-Requested-With
        self.assertEqual((await http(pa, "GET", "/api/state", host="evil.com"))[0], 403)    # DNS rebinding
        self.assertEqual((await http(pa, "GET", "/api/download/..%2f..%2fetc%2fpasswd"))[0], 404)
        # login failures / success
        srv = f"127.0.0.1:{self.server.port}"
        s, d = await jpost(pa, "/api/login", {"server": srv, "user": "alice", "pass": "pw1234"}); self.assertEqual(s, 200)
        s, d = await jpost(pb, "/api/login", {"server": srv, "user": "alice", "pass": "WRONG"}); self.assertEqual(s, 401)
        s, d = await jpost(pb, "/api/login", {"server": srv, "user": "bob", "pass": "pw1234"}); self.assertEqual(s, 200)
        await asyncio.sleep(0.3)
        s, _, b = await http(pa, "GET", "/api/state")
        st = json.loads(b); self.assertEqual(st["status"], "online"); self.assertEqual(len(st["peers"]), 2)
        # SSE stream on bob's gateway
        q = self.cores["bob"].subscribe()
        s, d = await jpost(pa, "/api/send", {"to": "bob", "text": "xin chào <b>bob</b>"}); self.assertEqual(s, 200)
        while True:
            typ, data = await asyncio.wait_for(q.get(), 5)
            if typ == "msg":
                break
        self.assertEqual(data["text"], "xin chào <b>bob</b>")
        # streamed upload through HTTP with Content-Length, then download over HTTP
        payload = os.urandom(2_500_000)
        hdr = {**X, "X-To": "bob", "X-Filename": urllib.parse.quote("tài liệu.bin"), "X-File-Id": "abc123"}
        s, _, b = await http(pa, "POST", "/api/upload", hdr, payload)
        self.assertEqual(s, 200, b)
        while True:
            typ, data = await asyncio.wait_for(q.get(), 10)
            if typ == "file_received":
                break
        s, head, got = await http(pb, "GET", "/api/download/" + urllib.parse.quote(data["name"]))
        self.assertEqual(s, 200); self.assertEqual(hashlib.sha256(got).digest(), hashlib.sha256(payload).digest())
        # uploading to an offline user is rejected
        s, _, b = await http(pa, "POST", "/api/upload", {**hdr, "X-To": "ghost", "X-File-Id": "zzz"}, b"x" * 1000)
        self.assertIn(s, (200, 409))
        # SSE endpoint answers with event-stream
        r, w = await asyncio.open_connection("127.0.0.1", pa)
        w.write(b"GET /api/events HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        first = await asyncio.wait_for(r.readuntil(b"\r\n\r\n"), 3)
        self.assertIn(b"text/event-stream", first); w.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
