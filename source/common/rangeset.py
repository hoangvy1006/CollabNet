"""Set of integers stored as sorted, disjoint, half-open intervals [start, end).

Used for (a) received packet numbers -> ACK ranges / duplicate detection and
(b) acknowledged byte ranges of a send stream -> selective retransmission.

Tiếng Việt: cấu trúc dữ liệu dùng chung cho hai việc nóng nhất của transport:
  * tập packet number đã nhận -> sinh dải ACK và phát hiện gói trùng/replay;
  * tập byte đã được ACK của một stream -> chỉ gửi lại đúng phần còn thiếu.
Mọi khoảng được gộp ngay khi thêm nên số khoảng luôn nhỏ, dù đã nhận hàng nghìn gói.
"""


class RangeSet:
    """Tập số nguyên lưu dưới dạng các khoảng nửa mở [start, end) đã sắp xếp, không giao nhau.

    Số khoảng thường rất nhỏ (các khoảng liền kề được gộp), nên các thao tác tuyến tính vẫn rẻ.
    """
    __slots__ = ("r",)

    def __init__(self):
        self.r = []  # list[(start, end)] ascending

    def add(self, s: int, e: int) -> None:
        # Thêm [s, e) và gộp với mọi khoảng chồng lấn hoặc liền kề.
        if s >= e:
            return
        out, placed = [], False
        for a, b in self.r:
            if b < s:
                out.append((a, b))
            elif a > e:
                if not placed:
                    out.append((s, e))
                    placed = True
                out.append((a, b))
            else:  # overlapping or adjacent -> merge
                s, e = min(s, a), max(e, b)
        if not placed:
            out.append((s, e))
        self.r = out

    def contains(self, x: int) -> bool:
        # Kiểm tra một packet number đã xuất hiện chưa (dùng để loại gói trùng và chống replay).
        return any(a <= x < b for a, b in self.r)

    def missing(self, s: int, e: int):
        """Sub-intervals of [s, e) that are NOT in the set.

        Trả về các đoạn còn thiếu trong [s, e) — chính là các đoạn cần gửi lại hoặc chưa nhận được.
        """
        res, cur = [], s
        for a, b in self.r:
            if b <= cur:
                continue
            if a >= e:
                break
            if a > cur:
                res.append((cur, min(a, e)))
            cur = max(cur, b)
            if cur >= e:
                break
        if cur < e:
            res.append((cur, e))
        return res

    def contiguous_end(self, start: int) -> int:
        """End of the interval containing `start` (or `start` if not covered).

        Dùng để biết đã nhận liền mạch tới đâu, từ đó mới giải phóng bộ đệm gửi (phần trước `start`).
        """
        for a, b in self.r:
            if a <= start < b:
                return b
            if a > start:
                break
        return start

    def prune_oldest(self, max_ranges: int):
        # Giới hạn bộ nhớ: bỏ các khoảng thấp nhất. Gói có số thứ tự dưới "floor" trả về coi như đã thấy (chống replay).
        """Drop the lowest ranges beyond `max_ranges`; returns the new floor (0 if nothing dropped)."""
        floor = 0
        while len(self.r) > max_ranges:
            floor = self.r.pop(0)[1]
        return floor
