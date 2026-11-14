"""Wire format of the CollabNet transport (a small QUIC-like protocol over UDP).

Datagram layout::

    +------+-----------+------------------+------------------------------+----------+
    | type | dest_cid  |  packet number   |  encrypted frames (AES-GCM)  | GCM tag  |
    | 1 B  |   4 B     |       8 B        |          variable            |  16 B    |
    +------+-----------+------------------+------------------------------+----------+
    \\_________ header (13 B, authenticated as AAD) _________/

Frames (inside the encrypted payload)::

    STREAM  0x02/0x03(FIN)  stream_id:4  offset:8  length:2  data
    ACK     0x04            largest:8 ack_delay_us:4 n:1  n x (range_start:8 range_end:8)
    MAX_STREAM_DATA 0x05    stream_id:4  max_offset:8       (flow-control credit)
    PING    0x06
    CLOSE   0x07            code:2 reason_len:2 reason
"""
# Tiếng Việt: module định nghĩa khuôn dạng gói tin của tầng transport tự viết (giống QUIC thu nhỏ).
# Mỗi datagram UDP = header 13 byte (loại gói, connection id đích, số thứ tự gói) + payload mã hoá AES-GCM.
# Payload là chuỗi "frame" (STREAM / ACK / MAX_STREAM_DATA / PING / CLOSE). Header được xác thực như AAD nên
# kẻ tấn công không thể sửa số thứ tự gói hay connection id mà không bị phát hiện.
import struct

MAX_DATAGRAM = 1200            # bytes on the wire; stays below typical MTU - headers
HDR = struct.Struct("!BIQ")    # type, destination connection id, packet number
HDR_LEN = HDR.size             # 13
TAG_LEN = 16

PT_INITIAL = 0x01              # client hello  (plaintext: client cid + X25519 public key)
PT_HANDSHAKE = 0x02            # server hello  (plaintext: server cid, key, signature)
PT_DATA = 0x10                 # encrypted application packet

FT_STREAM, FT_STREAM_FIN, FT_ACK, FT_MAX_STREAM_DATA, FT_PING, FT_CLOSE = 0x02, 0x03, 0x04, 0x05, 0x06, 0x07
STREAM_OVERHEAD = 15
MAX_PAYLOAD = MAX_DATAGRAM - HDR_LEN - TAG_LEN


def enc_stream(sid: int, off: int, data: bytes, fin: bool) -> bytes:
    # Frame STREAM: mang `data` tại vị trí `off` của stream `sid`; cờ FIN đánh dấu byte cuối của stream.
    return struct.pack("!BIQH", FT_STREAM_FIN if fin else FT_STREAM, sid, off, len(data)) + data


def enc_ack(ranges, delay_us: int) -> bytes:
    """ranges: list of inclusive (start, end) packet-number ranges, highest first."""
    # Frame ACK có chọn lọc (SACK): báo các khoảng packet number đã nhận để bên gửi chỉ gửi lại phần thiếu.
    # `delay_us` là thời gian bên nhận giữ ACK, dùng để hiệu chỉnh RTT.
    out = bytearray(struct.pack("!BQIB", FT_ACK, ranges[0][1], delay_us, len(ranges)))
    for s, e in ranges:
        out += struct.pack("!QQ", s, e)
    return bytes(out)


def enc_max_stream_data(sid: int, max_off: int) -> bytes:
    # Cấp thêm "credit" flow-control: bên nhận cam kết chấp nhận mọi byte tới `max_off` của stream `sid`.
    return struct.pack("!BIQ", FT_MAX_STREAM_DATA, sid, max_off)


def enc_ping() -> bytes:
    # Frame rỗng: keep-alive khi rảnh hoặc probe khi PTO. Vì là frame "ack-eliciting" nên ép bên kia trả ACK,
    # nhờ đó hai phía phát hiện được kết nối đã chết.
    return bytes([FT_PING])


def enc_close(code: int, reason: str) -> bytes:
    # Lý do bị cắt còn 200 byte để frame luôn nằm gọn trong một datagram (không cần phân mảnh tầng ứng dụng).
    r = reason.encode()[:200]
    return struct.pack("!BHH", FT_CLOSE, code, len(r)) + r


def decode_frames(buf: bytes):
    """Return a list of tuples; raises ValueError on malformed input.

    ('S', sid, off, data, fin) | ('A', ranges, delay_us) | ('M', sid, max) | ('P',) | ('C', code, reason)
    """
    # Dữ liệu đến từ mạng nên không được tin: mọi độ dài/khoảng đều được kiểm tra, sai định dạng -> ValueError
    # (connection sẽ đóng với mã "malformed frame" thay vì đọc tràn buffer).
    i, n, out = 0, len(buf), []
    try:
        while i < n:
            t = buf[i]
            if t in (FT_STREAM, FT_STREAM_FIN):
                sid, off, ln = struct.unpack_from("!IQH", buf, i + 1)
                i += STREAM_OVERHEAD
                if i + ln > n:
                    raise ValueError("truncated stream frame")
                out.append(("S", sid, off, bytes(buf[i:i + ln]), t == FT_STREAM_FIN))
                i += ln
            elif t == FT_ACK:
                _largest, delay, cnt = struct.unpack_from("!QIB", buf, i + 1)
                i += 14
                if cnt == 0:
                    raise ValueError("empty ack")
                ranges = []
                for _ in range(cnt):
                    s, e = struct.unpack_from("!QQ", buf, i)
                    i += 16
                    if e < s:
                        raise ValueError("bad ack range")
                    ranges.append((s, e))
                out.append(("A", ranges, delay))
            elif t == FT_MAX_STREAM_DATA:
                sid, mx = struct.unpack_from("!IQ", buf, i + 1)
                i += 13
                out.append(("M", sid, mx))
            elif t == FT_PING:
                i += 1
                out.append(("P",))
            elif t == FT_CLOSE:
                code, rl = struct.unpack_from("!HH", buf, i + 1)
                i += 5
                if i + rl > n:
                    raise ValueError("truncated close frame")
                out.append(("C", code, bytes(buf[i:i + rl]).decode(errors="replace")))
                i += rl
            else:
                raise ValueError(f"unknown frame type {t}")
    except struct.error as exc:
        raise ValueError(str(exc))
    return out
