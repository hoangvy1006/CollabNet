"""Giao thức tầng ứng dụng (chạy *bên trong* các stream của transport).

Mỗi thông điệp ứng dụng là ``u32 độ dài`` + một object JSON UTF-8, bắt buộc có trường ``"t"`` (loại).

Bước 0 — bắt tay TCP (trước mọi gói UDP), cùng số cổng với server nhưng là socket TCP:
    client -> server : {"t":"HELLO","proto":1,"user":..}
    server -> client : {"t":"HELLO_ACK","proto":1,"udp_port":..,"fp":<fingerprint Ed25519>,"ts":..}
    rồi đóng TCP. Client dùng `udp_port` trong ACK để mở kết nối UDP mã hoá (INITIAL/HANDSHAKE) bên dưới.

Cách dùng stream (chìa khoá để không bị head-of-line blocking):
    stream 0 của client : điều khiển (AUTH, LIST, BYE)                          sống lâu
    stream 1 của server : điều khiển (AUTH_OK/FAIL, PEERS, HISTORY, SENT, ERR)  sống lâu
    mỗi tin nhắn mở một stream mới : {"t":"MSG", ...}                     FIN sau khi gửi xong tin
    mỗi file mở một stream mới     : {"t":"FILE",...} + byte thô + {"t":"FILE_END","sha256":..}  FIN
                                       (P2P: mở trên kết nối TRỰC TIẾP giữa hai client, không qua server;
                                        chat chung = người gửi mở một kết nối P2P tới từng người đang online.
                                        {"t":"FILE_LOG"} trên stream điều khiển chỉ ghi thẻ file vào lịch sử.)
"""
import json
import re
import struct
import os

MAX_MSG = 1 << 20                 # kích thước tối đa của MỘT thông điệp JSON (chặn client gửi độ dài khổng lồ)
MAX_TEXT = 8192
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{2,24}$")
DISCOVERY_PORT = 9998
PROTO_VERSION = 1                 # phiên bản giao thức, kiểm tra trong bắt tay TCP HELLO / HELLO_ACK
TCP_HELLO_TIMEOUT = 5.0           # giây: thời gian tối đa cho một lượt HELLO -> HELLO_ACK trên TCP


class ProtocolError(Exception):
    """Dữ liệu vi phạm giao thức ứng dụng: bên nhận đóng kết nối với lỗi thay vì cố diễn giải."""


def pack(obj: dict) -> bytes:
    raw = json.dumps(obj, separators=(",", ":")).encode()
    return struct.pack("!I", len(raw)) + raw


class MsgBuffer:
    """Bộ giải mã tăng dần cho thông điệp JSON có tiền tố độ dài, có thể "trưng dụng" byte thô cho thân file.

    Dữ liệu stream đến theo từng mảnh bất kỳ nên không đảm bảo trùng ranh giới thông điệp: `feed` gom byte,
    `pop` chỉ trả thông điệp khi đã đủ. Với file, sau thông điệp FILE phần thân là byte thô nên dùng `take`.
    """

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


# Tên thiết bị đặc biệt của Windows: không thể tạo file có tên (hoặc phần trước dấu chấm đầu tiên) như vậy.
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def safe_filename(name: str) -> str:
    """Làm sạch tên file do người gửi cung cấp: bỏ đường dẫn, ký tự cấm, tên thiết bị Windows; giới hạn 120 ký tự."""
    name = os.path.basename(str(name).replace("\\", "/"))
    name = re.sub(r"[\x00-\x1f<>:\"|?*]", "_", name).strip(". ")
    if name.split(".", 1)[0].upper() in _WINDOWS_RESERVED:
        name = "_" + name                     # vd. "nul.txt" -> "_nul.txt" (mở "nul.txt" trên Windows sẽ thất bại)
    return name[:120] or "file"
