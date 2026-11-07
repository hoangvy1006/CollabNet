"""Set of integers stored as sorted, disjoint, half-open intervals [start, end).

Used for (a) received packet numbers -> ACK ranges / duplicate detection and
(b) acknowledged byte ranges of a send stream -> selective retransmission.
"""


class RangeSet:
    __slots__ = ("r",)

    def __init__(self):
        self.r = []  # list[(start, end)] ascending

    def add(self, s: int, e: int) -> None:
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
        return any(a <= x < b for a, b in self.r)

    def missing(self, s: int, e: int):
        """Sub-intervals of [s, e) that are NOT in the set."""
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
        """End of the interval containing `start` (or `start` if not covered)."""
        for a, b in self.r:
            if a <= start < b:
                return b
            if a > start:
                break
        return start

    def prune_oldest(self, max_ranges: int):
        """Drop the lowest ranges beyond `max_ranges`; returns the new floor (0 if nothing dropped)."""
        floor = 0
        while len(self.r) > max_ranges:
            floor = self.r.pop(0)[1]
        return floor
