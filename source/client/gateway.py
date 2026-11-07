"""Local HTTP gateway between the browser UI and ClientCore.

A tiny HTTP/1.1 server written directly on asyncio TCP streams (no web framework, no WebSocket):
  * static files for the UI (pure client-side JavaScript)
  * JSON API (fetch/XHR)            * Server-Sent Events for live updates (plain HTTP)
  * streamed file upload with back-pressure into the UDP transport

Security: bound to 127.0.0.1 by default, Host header check (DNS-rebinding), and a custom
`X-Requested-With` header is required on every POST (blocks cross-site form posts).
"""
import asyncio
import json
import mimetypes
import os
import urllib.parse

from common.discovery import discover
from common.protocol import MAX_TEXT, safe_filename

from .core import AuthError

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
STATIC = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
FONT_DIR = os.path.join(WEB_DIR, "fonts")
FONTS = {f"/fonts/{n}" for n in os.listdir(FONT_DIR) if n.endswith(".woff2")} if os.path.isdir(FONT_DIR) else set()
INLINE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
                ".webp": "image/webp"}       # previewed inline in chat; everything else is a forced download
CSP = "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; object-src 'none'; base-uri 'none'"
MAX_UPLOAD = 2 * 1024 ** 3


class HttpError(Exception):
    def __init__(self, status, msg):
        super().__init__(msg)
        self.status, self.msg = status, msg


REASONS = {200: "OK", 400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
           409: "Conflict", 413: "Payload Too Large", 500: "Internal Server Error", 502: "Bad Gateway"}


class Gateway:
    def __init__(self, core, host="127.0.0.1", port=8080, default_server="127.0.0.1:9000"):
        self.core, self.host, self.port, self.default_server = core, host, port, default_server
        self.server = None

    async def start(self):
        self.server = await asyncio.start_server(self._handle, self.host, self.port)
        self.port = self.server.sockets[0].getsockname()[1]

    def close(self):
        if self.server:
            self.server.close()

    # ------------------------------------------------------------ HTTP plumbing
    async def _handle(self, reader, writer):
        try:
            req = await self._read_head(reader)
            if req is None:
                return
            method, target, headers = req
            if not self._host_ok(headers.get("host", "")):
                raise HttpError(403, "bad Host header")
            if method == "POST" and headers.get("x-requested-with") != "collabnet":
                raise HttpError(403, "missing X-Requested-With")
            url = urllib.parse.urlsplit(target)
            await self._route(method, url, headers, reader, writer)
        except HttpError as exc:
            await self._send_json(writer, {"ok": False, "error": exc.msg}, exc.status)
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        except Exception as exc:                       # never crash the gateway
            try:
                await self._send_json(writer, {"ok": False, "error": str(exc)}, 500)
            except Exception:
                pass
        finally:
            try:
                writer.close()
            except Exception:
                pass

    def _host_ok(self, header: str) -> bool:
        """Reject DNS-rebinding: the Host must be this loopback gateway, not an attacker name."""
        host = header.strip().lower()
        if host.startswith("["):
            end = host.find("]")
            name = host[:end + 1] if end > 0 else ""
        else:
            name = host.split(":", 1)[0]
        allowed = {"127.0.0.1", "localhost", "[::1]"}
        bound = (self.host or "").strip().lower()
        if bound and bound not in ("0.0.0.0", "::", "[::]"):
            allowed.add(bound if bound.startswith("[") or ":" not in bound else f"[{bound}]")
        return name in allowed

    async def _read_head(self, reader):
        line = await reader.readline()
        if not line:
            return None
        try:
            method, target, _ = line.decode("latin1").strip().split(" ", 2)
        except ValueError:
            raise HttpError(400, "bad request line")
        headers, total = {}, 0
        while True:
            l = await reader.readline()
            total += len(l)
            if l in (b"\r\n", b"\n", b""):
                break
            if total > 65536:
                raise HttpError(400, "headers too large")
            k, _, v = l.decode("latin1").partition(":")
            headers[k.strip().lower()] = v.strip()
        return method, target, headers

    async def _send(self, writer, status, body: bytes, ctype, extra=None):
        hdrs = {"Content-Type": ctype, "Content-Length": len(body), "Connection": "close", "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", **(extra or {})}
        head = [f"HTTP/1.1 {status} {REASONS.get(status, '')}"] + [f"{k}: {v}" for k, v in hdrs.items()]
        writer.write(("\r\n".join(head) + "\r\n\r\n").encode() + body)
        await writer.drain()

    async def _send_json(self, writer, obj, status=200):
        await self._send(writer, status, json.dumps(obj).encode(), "application/json")

    @staticmethod
    async def _read_json(reader, headers):
        n = int(headers.get("content-length", 0))
        if n > 1 << 20:
            raise HttpError(413, "body too large")
        try:
            return json.loads((await reader.readexactly(n)).decode() or "{}")
        except ValueError:
            raise HttpError(400, "invalid JSON")

    # ------------------------------------------------------------ routes
    async def _route(self, method, url, headers, reader, writer):
        core, path = self.core, url.path
        if method == "GET" and path in STATIC:
            with open(os.path.join(WEB_DIR, STATIC[path]), "rb") as fh:
                body = fh.read()
            ctype = (mimetypes.guess_type(STATIC[path])[0] or "text/plain") + "; charset=utf-8"
            return await self._send(writer, 200, body, ctype,
                                    {"Content-Security-Policy": CSP})
        if method == "GET" and path in FONTS:
            with open(os.path.join(FONT_DIR, path[len("/fonts/"):]), "rb") as fh:
                return await self._send(writer, 200, fh.read(), "font/woff2",
                                        {"Cache-Control": "public, max-age=604800, immutable"})
        if method == "GET" and path == "/api/state":
            snap = core.snapshot()
            snap["default_server"] = self.default_server
            return await self._send_json(writer, snap)
        if method == "GET" and path == "/api/events":
            return await self._sse(writer)
        if method == "GET" and path == "/api/discover":
            return await self._send_json(writer, {"servers": await discover(2.2)})
        if method == "GET" and path.startswith("/api/download/"):
            q = urllib.parse.parse_qs(url.query)
            return await self._download(writer, urllib.parse.unquote(path[len("/api/download/"):]),
                                        inline="inline" in q)
        if method == "POST" and path == "/api/login":
            d = await self._read_json(reader, headers)
            try:
                host, _, port = str(d.get("server", self.default_server)).rpartition(":")
                await core.login(host or "127.0.0.1", int(port), str(d.get("user", "")), str(d.get("pass", "")))
            except AuthError as exc:
                raise HttpError(401, str(exc))
            except (ConnectionError, OSError, asyncio.TimeoutError, ValueError) as exc:
                raise HttpError(502, str(exc) or "cannot reach server")
            return await self._send_json(writer, {"ok": True, "user": core.user})
        if method == "POST" and path == "/api/logout":
            await core.logout()
            return await self._send_json(writer, {"ok": True})
        if method == "POST" and path == "/api/send":
            d = await self._read_json(reader, headers)
            text = str(d.get("text", "")).strip()
            if not text:
                raise HttpError(400, "empty message")
            if len(text) > MAX_TEXT:
                raise HttpError(413, f"message too long (max {MAX_TEXT} characters)")
            try:
                mid = core.send_message(str(d.get("to", "*")), text)
            except ConnectionError as exc:
                raise HttpError(409, str(exc))
            return await self._send_json(writer, {"ok": True, "id": mid})
        if method == "POST" and path == "/api/upload":
            return await self._upload(headers, reader, writer)
        raise HttpError(404, "not found")

    async def _sse(self, writer):
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nCache-Control: no-store\r\n"
                     b"Connection: keep-alive\r\n\r\n")
        q = self.core.subscribe()
        try:
            while True:
                try:
                    typ, data = await asyncio.wait_for(q.get(), 15)
                    writer.write(f"event: {typ}\ndata: {json.dumps(data)}\n\n".encode())
                except asyncio.TimeoutError:
                    writer.write(b": keep-alive\n\n")
                await writer.drain()
        finally:
            self.core.unsubscribe(q)

    async def _download(self, writer, name, inline=False):
        path = self.core.open_download(name)
        if not path:
            raise HttpError(404, "file not found")
        size = os.path.getsize(path)
        quoted = urllib.parse.quote(os.path.basename(path))
        ctype = INLINE_TYPES.get(os.path.splitext(path)[1].lower()) if inline else None
        disp = "inline" if ctype else "attachment"
        writer.write((f"HTTP/1.1 200 OK\r\nContent-Type: {ctype or 'application/octet-stream'}\r\n"
                      f"Content-Length: {size}\r\nContent-Disposition: {disp}; filename*=UTF-8''{quoted}\r\n"
                      f"X-Content-Type-Options: nosniff\r\nContent-Security-Policy: sandbox\r\n"
                      f"Cache-Control: private, max-age=3600\r\nConnection: close\r\n\r\n").encode())
        with open(path, "rb") as fh:
            while chunk := fh.read(65536):
                writer.write(chunk)
                await writer.drain()

    async def _upload(self, headers, reader, writer):
        try:
            size = int(headers.get("content-length", ""))
        except ValueError:
            raise HttpError(400, "Content-Length required")
        if size > MAX_UPLOAD:
            raise HttpError(413, "file too large")
        to = urllib.parse.unquote(headers.get("x-to", ""))
        name = safe_filename(urllib.parse.unquote(headers.get("x-filename", "file")))
        fid = headers.get("x-file-id") or None
        if not to or to == "*":
            raise HttpError(400, "choose a single recipient for file transfer")

        async def body():
            remaining = size
            while remaining > 0:
                data = await reader.read(min(65536, remaining))
                if not data:
                    raise ConnectionError("upload interrupted")
                remaining -= len(data)
                yield data
        try:
            fid = await self.core.send_file(to, name, size, body(), fid)
        except (ConnectionError, ValueError) as exc:
            raise HttpError(409, str(exc))
        await self._send_json(writer, {"ok": True, "id": fid})
