"""Application-layer protocol (runs *inside* transport streams).

Every application message is ``u32 length`` + UTF-8 JSON object with a mandatory ``"t"`` (type) field.

Stream usage (the key to avoiding head-of-line blocking):
    client stream 0   : control  (AUTH, LIST, BYE)                      long-lived
    server stream 1   : control  (AUTH_OK/FAIL, PEERS, SENT, ERR)       long-lived
    one new stream per chat message  : {"t":"MSG", ...}                 FIN after the message
    one new stream per file transfer : {"t":"FILE",...} + raw bytes + {"t":"FILE_END","sha256":..}  FIN
"""
import json
import re
import struct
import os

MAX_MSG = 1 << 20
MAX_TEXT = 8192
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{2,24}$")
DISCOVERY_PORT = 9998


class ProtocolError(Exception):
    pass


def pack(obj: dict) -> bytes:
    raw = json.dumps(obj, separators=(",", ":")).encode()
    return struct.pack("!I", len(raw)) + raw


class MsgBuffer:
    """Incremental decoder of length-prefixed JSON messages, with raw-byte take-over for file bodies."""

    def __init__(self):
        self.buf = bytearray()

    def feed(self, data: bytes):
        self.buf += data

    def pop(self):
        if len(self.buf) < 4:
            return None
        (n,) = struct.unpack_from("!I", self.buf)
        if n > MAX_MSG:
            raise ProtocolError("message too large")
        if len(self.buf) < 4 + n:
            return None
        raw = bytes(self.buf[4:4 + n])
        del self.buf[:4 + n]
        try:
            obj = json.loads(raw.decode())
        except ValueError:
            raise ProtocolError("invalid JSON")
        if not isinstance(obj, dict) or not isinstance(obj.get("t"), str):
            raise ProtocolError("missing message type")
        return obj

    def take(self, n: int) -> bytes:
        d = bytes(self.buf[:n])
        del self.buf[:n]
        return d

    def take_all(self) -> bytes:
        return self.take(len(self.buf))


def safe_filename(name: str) -> str:
    name = os.path.basename(str(name).replace("\\", "/"))
    name = re.sub(r"[\x00-\x1f<>:\"|?*]", "_", name).strip(". ")
    return name[:120] or "file"
