"""Congestion controllers: CUBIC (RFC 8312 / 9438 style) and a compact BBR (v1).

Both implement the same interface so the transport can switch with `--cc`.
Units: bytes, seconds, bytes/second.  One "segment" == one datagram (MSS).
"""
import random
from collections import deque

from .packet import MAX_DATAGRAM

# Tiếng Việt: kiểm soát tắc nghẽn quyết định bên gửi được phép có bao nhiêu byte "đang bay" (cwnd) và gửi nhanh
# tới đâu (pacing). Hai thuật toán dùng chung giao diện nên transport chọn bằng tham số `--cc`:
#   * CUBIC: dựa trên mất gói, cwnd tăng theo hàm bậc ba quanh điểm w_max (mức cwnd lúc mất gói gần nhất).
#   * BBR v1: dựa trên mô hình đường truyền (băng thông nghẽn BtlBw, RTT nhỏ nhất RTprop), ít nhạy với mất gói.
MSS = MAX_DATAGRAM
INITIAL_CWND = 10 * MSS
MIN_CWND = 2 * MSS


class RateSample:
    """Delivery-rate sample attached to every newly acknowledged packet.

    `rate` (byte/s) là tốc độ giao hàng đo được, `prior_delivered` dùng để đếm vòng (round) cho BBR,
    `app_limited` cho biết ứng dụng không còn dữ liệu để gửi (khi đó không nên tăng cwnd).
    """
    __slots__ = ("rate", "prior_delivered", "app_limited")

    def __init__(self, rate, prior_delivered, app_limited):
        self.rate, self.prior_delivered, self.app_limited = rate, prior_delivered, app_limited


class CongestionControl:
    """Giao diện chung. transport gọi: on_sent (gửi gói), on_ack (gói được ACK), on_congestion (phát hiện mất gói),
    on_persistent_congestion (nhiều lần PTO liên tiếp) và pacing_rate (tốc độ phát tối đa, byte/s)."""
    name = "base"

    def __init__(self):
        self.cwnd = float(INITIAL_CWND)
        self.state = ""

    def on_sent(self, now, size, inflight): ...
    def on_ack(self, now, size, sent_time, rtt, sample, inflight, srtt): ...
    def on_congestion(self, now, sent_time_of_lost): ...
    def on_persistent_congestion(self, now): ...
    def pacing_rate(self, srtt): return None


# ------------------------------------------------------------------ CUBIC
class Cubic(CongestionControl):
    """W(t) = C (t-K)^3 + Wmax, multiplicative decrease by BETA, TCP-friendly region, fast convergence.

    Cwnd tăng theo hàm bậc ba của thời gian kể từ lần mất gói gần nhất: đầu chu kỳ tăng nhanh để lấy lại
    băng thông cũ (Wmax), gần Wmax thì tăng chậm để thăm dò nhẹ nhàng. `w_est` là nhánh "Reno-friendly"
    để CUBIC không chiếm quá nhiều so với TCP khi RTT lớn.
    """
    name = "cubic"
    C, BETA = 0.4, 0.7

    def __init__(self):
        super().__init__()
        self.ssthresh = float("inf")
        self.w_max = 0.0          # segments
        self.k = 0.0
        self.epoch = None
        self.w_est = 0.0
        self.recovery_start = -1.0
        self.state = "slow-start"

    def on_ack(self, now, size, sent_time, rtt, sample, inflight, srtt):
        if sent_time <= self.recovery_start:       # still in the recovery period of the last loss
            return
        if sample is not None and sample.app_limited and inflight + size < self.cwnd * 0.5:
            return                                   # do not grow cwnd when the sender is not using it
        if self.cwnd < self.ssthresh:                # slow start
            self.cwnd += size
            self.state = "slow-start"
            return
        self.state = "cubic"
        cw = self.cwnd / MSS
        if self.epoch is None:
            self.epoch = now
            if cw < self.w_max:
                self.k = ((self.w_max - cw) / self.C) ** (1 / 3)
            else:
                self.k, self.w_max = 0.0, cw
            self.w_est = cw
        t = now - self.epoch + (srtt or 0.0)
        target = self.C * (t - self.k) ** 3 + self.w_max
        self.w_est += 3 * (1 - self.BETA) / (1 + self.BETA) * (size / MSS) / cw   # Reno-friendly estimate
        target = min(max(target, self.w_est), 1.5 * cw)
        if target > cw:
            inc = (target - cw) / cw * (size / MSS)
        else:
            inc = 0.01 * (size / MSS) / cw
        self.cwnd += inc * MSS

    def on_congestion(self, now, sent_time_of_lost):
        # Giảm cwnd nhân (x BETA) đúng một lần mỗi vòng RTT: nhiều gói mất cùng một đợt chỉ tính là một sự kiện.
        if sent_time_of_lost <= self.recovery_start:
            return                                   # one reduction per round trip
        self.recovery_start = now
        cw = self.cwnd / MSS
        self.w_max = cw * (1 + self.BETA) / 2 if cw < self.w_max else cw   # fast convergence
        self.cwnd = max(self.cwnd * self.BETA, MIN_CWND)
        self.ssthresh = self.cwnd
        self.epoch = None
        self.state = "recovery"

    def on_persistent_congestion(self, now):
        self.ssthresh = max(self.cwnd * self.BETA, MIN_CWND)
        self.cwnd = float(MIN_CWND)
        self.epoch = None
        self.recovery_start = now
        self.state = "persistent-congestion"

    def pacing_rate(self, srtt):
        if not srtt:
            return None
        gain = 2.0 if self.cwnd < self.ssthresh else 1.25
        return gain * self.cwnd / srtt


# ------------------------------------------------------------------ BBR
class Bbr(CongestionControl):
    """BBR v1: model the path with BtlBw (max filter) and RTprop (min filter).

    STARTUP -> DRAIN -> PROBE_BW (gain cycle) with periodic PROBE_RTT.
    Loss is *not* used as a congestion signal (like BBRv1).

    Ý tưởng: ước lượng băng thông nút cổ chai (BtlBw) và RTT nhỏ nhất (RTprop) rồi gửi đúng
    BtlBw x RTprop byte "đang bay" — không coi mất gói là tín hiệu tắc nghẽn. Vì vậy BBR cần mẫu tốc độ
    giao hàng chính xác; nếu mẫu bị đánh giá thấp, cwnd và pacing cùng nhỏ lại và thuật toán tự hạn chế.
    """
    name = "bbr"
    HIGH_GAIN = 2.885
    CYCLE = (1.25, 0.75, 1, 1, 1, 1, 1, 1)
    BW_WINDOW = 10                         # số round giữ mẫu băng thông để lấy max (BtlBw)

    def __init__(self):
        super().__init__()
        self.state = "STARTUP"
        self.pacing_gain = self.cwnd_gain = self.HIGH_GAIN
        # Bộ lọc max theo cửa sổ: deque đơn điệu giảm các (round, rate). Đầu deque luôn là max của cửa sổ,
        # nên mỗi ACK tốn O(1) khấu hao thay vì quét lại toàn bộ mẫu (trước đây O(số mẫu) cho mỗi gói).
        self.samples = deque()
        self.btl_bw = 0.0
        self.min_rtt = float("inf")
        self.min_rtt_stamp = None
        self.delivered = 0
        self.round = 0
        self.next_round_delivered = 0
        self.full_bw, self.full_cnt, self.full_pipe = 0.0, 0, False
        self.cycle_idx, self.cycle_stamp = 0, 0.0
        self.probe_rtt_done = None

    def bdp(self):
        # Bandwidth-Delay Product = BtlBw x RTprop: lượng byte tối ưu để "lấp đầy ống" mà không gây hàng đợi.
        return self.btl_bw * self.min_rtt if self.min_rtt != float("inf") else 0.0

    def _enter_probe_bw(self, now):
        self.state = "PROBE_BW"
        self.cwnd_gain = 2.0
        self.cycle_idx = random.choice([0] + list(range(2, 8)))
        self.pacing_gain = self.CYCLE[self.cycle_idx]
        self.cycle_stamp = now

    def on_ack(self, now, size, sent_time, rtt, sample, inflight, srtt):
        # Mỗi "round" kết thúc khi một gói gửi sau mốc `next_round_delivered` được ACK (~ một vòng RTT).
        self.delivered += size
        round_start = False
        if sample is not None:
            if sample.prior_delivered >= self.next_round_delivered:
                self.next_round_delivered = self.delivered
                self.round += 1
                round_start = True
            if sample.rate > 0 and (not sample.app_limited or sample.rate >= self.btl_bw):
                while self.samples and self.samples[-1][1] <= sample.rate:
                    self.samples.pop()             # mẫu cũ không lớn hơn mẫu mới thì không bao giờ là max nữa
                self.samples.append((self.round, sample.rate))
        while self.samples and self.samples[0][0] < self.round - self.BW_WINDOW:
            self.samples.popleft()                 # mẫu đã trượt khỏi cửa sổ
        self.btl_bw = self.samples[0][1] if self.samples else 0.0

        expired = self.min_rtt_stamp is not None and now - self.min_rtt_stamp > 10.0
        if rtt is not None and (rtt <= self.min_rtt or expired):
            self.min_rtt, self.min_rtt_stamp = rtt, now

        # --- state machine
        if self.state == "STARTUP" and round_start and sample is not None and not sample.app_limited:
            if self.btl_bw >= self.full_bw * 1.25:
                self.full_bw, self.full_cnt = self.btl_bw, 0
            else:
                self.full_cnt += 1
                if self.full_cnt >= 3:
                    self.full_pipe = True
                    self.state, self.pacing_gain = "DRAIN", 1 / self.HIGH_GAIN
        if self.state == "DRAIN" and inflight <= self.bdp():
            self._enter_probe_bw(now)
        elif self.state == "PROBE_BW" and self.min_rtt != float("inf") and now - self.cycle_stamp > self.min_rtt:
            self.cycle_idx = (self.cycle_idx + 1) % len(self.CYCLE)
            self.pacing_gain = self.CYCLE[self.cycle_idx]
            self.cycle_stamp = now
        if expired and self.state != "PROBE_RTT":
            self.state, self.pacing_gain, self.probe_rtt_done = "PROBE_RTT", 1.0, None
        if self.state == "PROBE_RTT":
            if self.probe_rtt_done is None and inflight <= 4 * MSS:
                self.probe_rtt_done = now + max(0.2, self.min_rtt if self.min_rtt != float("inf") else 0.2)
            elif self.probe_rtt_done is not None and now >= self.probe_rtt_done:
                self.min_rtt_stamp = now
                if self.full_pipe:
                    self._enter_probe_bw(now)
                else:
                    self.state, self.pacing_gain, self.cwnd_gain = "STARTUP", self.HIGH_GAIN, self.HIGH_GAIN

        # --- cwnd
        target = self.cwnd_gain * self.bdp() + 3 * MSS
        if self.state == "PROBE_RTT":
            self.cwnd = 4 * MSS
        elif self.full_pipe:
            self.cwnd = min(self.cwnd + size, target)
        elif self.cwnd < target or self.delivered < INITIAL_CWND:
            self.cwnd += size
        self.cwnd = max(self.cwnd, 4 * MSS)

    def on_congestion(self, now, sent_time_of_lost):
        # BBRv1 ignores loss in steady state. During STARTUP the 2.885x gain
        # overshoots a 1-5% lossy path, so leave STARTUP on the first loss round.
        if self.state == "STARTUP":
            self.full_pipe = True
            self.state, self.pacing_gain = "DRAIN", 1 / self.HIGH_GAIN

    def on_persistent_congestion(self, now):
        self.cwnd = float(4 * MSS)
        if self.state == "STARTUP":
            self.full_pipe = True
            self.state, self.pacing_gain = "DRAIN", 1 / self.HIGH_GAIN

    def pacing_rate(self, srtt):
        if self.btl_bw > 0:
            return self.pacing_gain * self.btl_bw
        return self.HIGH_GAIN * self.cwnd / srtt if srtt else None


def make_cc(name: str) -> CongestionControl:
    # Chọn thuật toán theo tham số --cc; tên lạ bị từ chối sớm thay vì âm thầm dùng mặc định.
    name = (name or "cubic").lower()
    if name == "cubic":
        return Cubic()
    if name == "bbr":
        return Bbr()
    raise ValueError(f"unknown congestion control '{name}' (use cubic or bbr)")
