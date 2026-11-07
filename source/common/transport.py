"""CollabNet transport: reliable, encrypted, multi-stream delivery on top of raw UDP sockets.

Design (inspired by QUIC / Valve GameNetworkingSocket):

* The UDP layer only moves *datagrams*.  Reliability lives here, in user space.
* Many independent unidirectional **streams** share one connection.  Every chat
  message and every file is its own stream, so a lost packet of a big file never
  blocks a chat message (no head-of-line blocking across streams).
* Every packet carries a **new, monotonically increasing packet number** (also on
  retransmission).  ACK frames carry ranges (SACK) -> only the *missing* byte
  ranges are retransmitted.
* Loss detection: packet threshold (3) + time threshold (9/8 RTT) + PTO timer.
* Flow control: per-stream credit (MAX_STREAM_DATA) = sliding receive window.
* Congestion control: pluggable CUBIC / BBR + pacing.
* Security: X25519 handshake signed by the server's Ed25519 key, AES-256-GCM per packet.
* Resilience: keep-alive PINGs, idle timeout, address migration, handshake retries.
"""
from __future__ import annotations

import asyncio
import bisect
import itertools
import logging
import os
import random
import socket
import struct

from . import crypto
from .congestion import RateSample, make_cc
from .packet import (HDR, HDR_LEN, MAX_PAYLOAD, PT_DATA, PT_HANDSHAKE, PT_INITIAL, STREAM_OVERHEAD, TAG_LEN,
                     decode_frames, enc_ack, enc_close, enc_max_stream_data, enc_ping, enc_stream)
from .rangeset import RangeSet

log = logging.getLogger("collabnet.transport")

STREAM_WINDOW = 512 * 1024      # initial / rolling per-stream receive window
MAX_ACK_DELAY = 0.025
GRANULARITY = 0.001
INITIAL_RTT = 0.25
IDLE_TIMEOUT = 20.0
KEEPALIVE_INTERVAL = 4.0
SEND_BUF_HIGH = 256 * 1024      # app writers should wait (drain) above this
SEND_BUF_LOW = 64 * 1024
MAX_RECV_STREAMS = 1024
PKT_THRESHOLD = 3
TIME_THRESHOLD = 9 / 8
MAX_ACK_RANGES = 6
MAX_TRACKED_RANGES = 64


# ====================================================================== streams
class SendStream:
    """Sender side of a stream: byte buffer + selective-retransmission bookkeeping."""

    def __init__(self, sid: int, priority: int = 0):
        self.sid, self.priority, self.served = sid, priority, 0
        self.base = 0                    # stream offset of data[0] (everything before is acked)
        self.data = bytearray()          # unacked + unsent bytes
        self.next = 0                    # next never-sent offset
        self.fin_offset = None
        self.fin_sent = self.fin_acked = False
        self.retx: list[tuple[int, int]] = []   # byte ranges declared lost
        self.acked = RangeSet()
        self.max_data = STREAM_WINDOW    # peer's flow-control limit
        self.waiters: list[asyncio.Future] = []
        self.drain_cbs: list[tuple] = []   # (callback, release_below)
        self.done: asyncio.Future | None = None

    @property
    def total(self) -> int:
        return self.base + len(self.data)

    def buffered(self) -> int:
        return len(self.data)

    def has_data(self) -> bool:
        while self.retx and not self.acked.missing(*self.retx[0]):
            self.retx.pop(0)
        if self.retx:
            return True
        if self.next < min(self.total, self.max_data):
            return True
        return self.fin_offset is not None and not self.fin_sent and self.next >= self.fin_offset

    def next_frame(self, max_len: int):
        """Return (offset, bytes, fin) for the next STREAM frame, or None."""
        while self.retx:
            s, e = self.retx.pop(0)
            pieces = self.acked.missing(s, e)
            if not pieces:
                continue
            self.retx = pieces[1:] + self.retx
            a, b = pieces[0]
            n = min(b - a, max_len)
            if a + n < b:
                self.retx.insert(0, (a + n, b))
            fin = self.fin_offset is not None and a + n == self.fin_offset
            return a, bytes(self.data[a - self.base:a - self.base + n]), fin
        limit = min(self.total, self.max_data)
        if self.next < limit:
            n = min(limit - self.next, max_len)
            off = self.next
            self.next += n
            fin = self.fin_offset is not None and self.next == self.fin_offset
            self.fin_sent = self.fin_sent or fin
            return off, bytes(self.data[off - self.base:off - self.base + n]), fin
        if self.fin_offset is not None and not self.fin_sent and self.next == self.fin_offset:
            self.fin_sent = True
            return self.next, b"", True
        return None

    def on_acked(self, off: int, ln: int, fin: bool):
        self.acked.add(off, off + ln)
        if fin:
            self.fin_acked = True
        end = self.acked.contiguous_end(self.base)
        if end > self.base:
            del self.data[:end - self.base]
            self.base = end

    def on_lost(self, off: int, ln: int, fin: bool):
        if ln > 0:
            self.retx.append((off, off + ln))
        elif fin:
            self.fin_sent = False

    def complete(self) -> bool:
        return self.fin_acked and self.fin_offset is not None and self.base >= self.fin_offset


class RecvStream:
    """Receiver side: re-orders out-of-order segments, tracks the flow-control window."""

    def __init__(self, sid: int):
        self.sid = sid
        self.next = 0
        self.ooo: list[tuple[int, bytes]] = []
        self.fin_offset = None
        self.fin_delivered = False
        self.consumed = 0
        self.adv_max = STREAM_WINDOW
        self.dirty = False

    def receive(self, off: int, data: bytes, fin: bool) -> bytes:
        end = off + len(data)
        if end > self.adv_max:
            raise ValueError("flow-control violation")
        if fin:
            self.fin_offset = end
        parts = []
        if data and end > self.next:
            if off <= self.next:
                parts.append(data[self.next - off:])
                self.next = end
            else:
                bisect.insort(self.ooo, (off, data))
            while self.ooo and self.ooo[0][0] <= self.next:
                o, d = self.ooo.pop(0)
                if o + len(d) > self.next:
                    parts.append(d[self.next - o:])
                    self.next = o + len(d)
        return b"".join(parts)

    def finished(self) -> bool:
        return self.fin_offset is not None and self.next >= self.fin_offset


class SentPacket:
    __slots__ = ("pn", "time", "size", "frames", "delivered", "delivered_time", "first_sent", "app_limited")


# ================================================================== connection
class Connection:
    """One secure association between two endpoints (client <-> server)."""

    def __init__(self, ep: "Endpoint", is_client: bool, peer_addr, cid: int, peer_cid: int,
                 send_key: bytes, recv_key: bytes, cc: str = "cubic"):
        self.ep, self.loop, self.is_client = ep, ep.loop, is_client
        self.peer_addr, self.cid, self.peer_cid = peer_addr, cid, peer_cid
        self.send_cipher, self.recv_cipher = crypto.PacketCipher(send_key), crypto.PacketCipher(recv_key)
        self.cc = make_cc(cc)
        now = self.loop.time()
        # --- sending / loss recovery
        self.next_pn = 0
        self.sent: dict[int, SentPacket] = {}
        self.bytes_in_flight = 0
        self.largest_acked = -1
        self.srtt = self.rttvar = None
        self.min_rtt = float("inf")
        self.latest_rtt = INITIAL_RTT
        self.pto_count = 0
        self.loss_time = None
        self.last_ae_sent = now
        self.delivered, self.delivered_time, self.first_sent_time = 0, now, now
        self.pacing_next = 0.0
        self._pace_wait = False
        self.ping_pending = False
        # --- receiving
        self.recv_ranges = RangeSet()
        self.recv_floor = 0
        self.largest_recv = -1
        self.largest_recv_time = now
        self.ack_deadline = None
        self.ack_pending_count = 0
        # --- streams
        self.send_streams: dict[int, SendStream] = {}
        self.recv_streams: dict[int, RecvStream] = {}
        self.finished_recv: set[int] = set()
        self._next_sid = 0 if is_client else 1      # client opens even ids, server odd ids
        self._tick = itertools.count(1)
        # --- state
        self.closed = False
        self.close_reason = ""
        self.last_recv = self.last_send = now
        self._timer = None
        self._timer_when = None
        self._flush_scheduled = False
        self.on_stream_data = None   # (conn, sid, data, fin) -> None | False(=manual credit)
        self.on_close = None         # (conn, reason)
        self.user = None             # free slot for the application
        self.n_sent = self.n_lost = self.bytes_retx = 0
        self._update_timer()

    # ------------------------------------------------------------ public API
    def open_stream(self, priority: int = 0) -> int:
        sid = self._next_sid
        self._next_sid += 2
        ss = SendStream(sid, priority)
        ss.done = self.loop.create_future()
        self.send_streams[sid] = ss
        return sid

    def send(self, sid: int, data: bytes = b"", fin: bool = False):
        ss = self.send_streams.get(sid)
        if self.closed or ss is None:
            raise ConnectionError("connection/stream closed")
        if data:
            ss.data += data
        if fin:
            ss.fin_offset = ss.total
        self._schedule_flush()

    def buffered(self, sid: int) -> int:
        ss = self.send_streams.get(sid)
        return ss.buffered() if ss else 0

    def acked_offset(self, sid: int):
        ss = self.send_streams.get(sid)
        return ss.base if ss else None

    def set_drain_callback(self, sid: int, cb, below: int = SEND_BUF_LOW):
        """Fire `cb` once the stream buffer drops below `below` bytes.

        The relay uses its own high-water mark here. Waiting for the much
        smaller SEND_BUF_LOW stalls a transfer for the whole congestion window.
        """
        ss = self.send_streams.get(sid)
        if ss is None or self.closed or ss.buffered() < below:
            self.loop.call_soon(self._safe_cb, cb)
            return
        ss.drain_cbs.append((cb, below))

    @staticmethod
    def _safe_cb(cb):
        try:
            cb()
        except Exception:
            log.exception("drain callback failed")

    async def drain(self, sid: int):
        """Back-pressure: wait until the stream's send buffer is below the high-water mark."""
        ss = self.send_streams.get(sid)
        while ss is not None and ss.buffered() >= SEND_BUF_HIGH and not self.closed:
            fut = self.loop.create_future()
            ss.waiters.append(fut)
            await fut
        if self.closed:
            raise ConnectionError("connection closed")

    def send_done(self, sid: int):
        """Future that resolves True when every byte (and FIN) of the stream was acknowledged."""
        ss = self.send_streams.get(sid)
        if ss is None:
            fut = self.loop.create_future()
            fut.set_result(True)
            return fut
        return ss.done

    def consume(self, sid: int, n: int):
        """Tell the transport the application has processed `n` more bytes of stream `sid`."""
        rs = self.recv_streams.get(sid)
        if rs is None or n <= 0:
            return
        rs.consumed += n
        if rs.consumed + STREAM_WINDOW - rs.adv_max >= STREAM_WINDOW // 2:
            rs.adv_max = rs.consumed + STREAM_WINDOW
            rs.dirty = True
            self._schedule_flush()

    def close(self, code: int = 0, reason: str = ""):
        if self.closed:
            return
        payload = enc_close(code, reason)
        for _ in range(3):                      # best effort, CLOSE is not retransmitted
            self._send_packet(payload)
        self._terminate(f"closed locally: {reason}")

    def stats(self) -> dict:
        return {"cc": self.cc.name, "cc_state": self.cc.state,
                "srtt_ms": round((self.srtt or 0) * 1000, 2),
                "min_rtt_ms": round(self.min_rtt * 1000, 2) if self.min_rtt != float("inf") else 0,
                "cwnd": int(self.cc.cwnd), "in_flight": self.bytes_in_flight,
                "sent_pkts": self.n_sent, "lost_pkts": self.n_lost, "retx_bytes": self.bytes_retx}

    # ------------------------------------------------------------ receive path
    def on_datagram(self, hdr: bytes, pn: int, ct: bytes, addr):
        if self.closed:
            return
        try:
            pt = self.recv_cipher.open(pn, hdr, ct)
        except Exception:
            return                               # forged / corrupted -> silently dropped
        if pn < self.recv_floor or self.recv_ranges.contains(pn):
            return                               # replay / duplicate
        now = self.loop.time()
        self.last_recv = now
        if addr != self.peer_addr:
            log.info("peer address migrated %s -> %s", self.peer_addr, addr)
            self.peer_addr = addr
        prev_largest = self.largest_recv
        self.recv_ranges.add(pn, pn + 1)
        floor = self.recv_ranges.prune_oldest(MAX_TRACKED_RANGES)
        self.recv_floor = max(self.recv_floor, floor)
        if pn > self.largest_recv:
            self.largest_recv, self.largest_recv_time = pn, now
        try:
            frames = decode_frames(pt)
        except ValueError:
            self.close(2, "malformed frame")
            return
        ack_eliciting = False
        for f in frames:
            k = f[0]
            if k == "S":
                ack_eliciting = True
                self._on_stream_frame(f[1], f[2], f[3], f[4])
            elif k == "A":
                self._on_ack(f[1], f[2], now)
            elif k == "M":
                ack_eliciting = True
                ss = self.send_streams.get(f[1])
                if ss and f[2] > ss.max_data:
                    ss.max_data = f[2]
            elif k == "P":
                ack_eliciting = True
            elif k == "C":
                self._terminate(f"peer closed: {f[2]} (code {f[1]})")
            if self.closed:
                return
        if ack_eliciting:
            self.ack_pending_count += 1
            immediate = self.ack_pending_count >= 2 or pn != prev_largest + 1
            d = now if immediate else now + MAX_ACK_DELAY
            if self.ack_deadline is None or d < self.ack_deadline:
                self.ack_deadline = d
        self._flush()

    def _on_stream_frame(self, sid: int, off: int, data: bytes, fin: bool):
        if sid in self.finished_recv:
            return
        if (sid % 2 == 0) == self.is_client:     # that id parity belongs to *our* send streams
            return
        rs = self.recv_streams.get(sid)
        if rs is None:
            if len(self.recv_streams) >= MAX_RECV_STREAMS:
                self.close(3, "too many streams")
                return
            rs = self.recv_streams[sid] = RecvStream(sid)
        try:
            chunk = rs.receive(off, data, fin)
        except ValueError:
            self.close(3, "flow-control violation")
            return
        fin_now = rs.finished() and not rs.fin_delivered
        if not chunk and not fin_now:
            return
        rs.fin_delivered = rs.fin_delivered or fin_now
        auto = True
        if self.on_stream_data:
            try:
                auto = self.on_stream_data(self, sid, chunk, fin_now) is not False
            except Exception:
                log.exception("stream callback failed")
        if auto:
            self.consume(sid, len(chunk))
        if fin_now:
            self.recv_streams.pop(sid, None)
            self.finished_recv.add(sid)

    # ------------------------------------------------------------ ACK / loss handling
    def _on_ack(self, ranges, delay_us: int, now: float):
        if ranges[0][1] >= self.next_pn:
            return                                # acknowledges something we never sent
        acked = [p for pn, p in self.sent.items() if any(s <= pn <= e for s, e in ranges)]
        if not acked:
            return
        largest = max(p.pn for p in acked)
        rtt_for_cc = None
        if largest > self.largest_acked:
            self.largest_acked = largest
            p = next(p for p in acked if p.pn == largest)
            self.latest_rtt = now - p.time
            self.min_rtt = min(self.min_rtt, self.latest_rtt)
            adj = self.latest_rtt - min(delay_us / 1e6, MAX_ACK_DELAY)
            if adj < self.min_rtt:
                adj = self.latest_rtt
            if self.srtt is None:
                self.srtt, self.rttvar = adj, adj / 2
            else:
                self.rttvar = 0.75 * self.rttvar + 0.25 * abs(self.srtt - adj)
                self.srtt = 0.875 * self.srtt + 0.125 * adj
            rtt_for_cc = adj
        for p in sorted(acked, key=lambda x: x.pn):
            self._on_packet_acked(p, now, rtt_for_cc if p.pn == largest else None)
        self.pto_count = 0
        self._detect_loss(now)
        self._check_drain()

    def _on_packet_acked(self, p: SentPacket, now: float, rtt):
        del self.sent[p.pn]
        self.bytes_in_flight -= p.size
        self.delivered += p.size
        self.delivered_time = now
        self.first_sent_time = p.time
        interval = max(p.time - p.first_sent, now - p.delivered_time, 1e-6)
        sample = RateSample((self.delivered - p.delivered) / interval, p.delivered, p.app_limited)
        self.cc.on_ack(now, p.size, p.time, rtt, sample, self.bytes_in_flight, self.srtt)
        for f in p.frames:
            if f[0] == "S":
                ss = self.send_streams.get(f[1])
                if ss:
                    ss.on_acked(f[2], f[3], f[4])
                    if ss.complete():
                        self._finish_send_stream(ss)

    def _finish_send_stream(self, ss: SendStream):
        self.send_streams.pop(ss.sid, None)
        if ss.done and not ss.done.done():
            ss.done.set_result(True)
        self._release(ss)

    def _release(self, ss: SendStream):
        """Unblock every waiter. Used when the stream or the connection is finished."""
        for w in ss.waiters:
            if not w.done():
                w.set_result(None)
        ss.waiters = []
        cbs, ss.drain_cbs = ss.drain_cbs, []
        for cb, _below in cbs:
            self._safe_cb(cb)

    def _check_drain(self):
        for ss in list(self.send_streams.values()):
            buffered = ss.buffered()
            if ss.waiters and buffered < SEND_BUF_LOW:
                for w in ss.waiters:
                    if not w.done():
                        w.set_result(None)
                ss.waiters = []
            if not ss.drain_cbs:
                continue
            ready = [cb for cb, below in ss.drain_cbs if buffered < below]
            if not ready:
                continue
            ss.drain_cbs = [(cb, below) for cb, below in ss.drain_cbs if buffered >= below]
            for cb in ready:
                self._safe_cb(cb)

    def _detect_loss(self, now: float):
        if self.largest_acked < 0:
            return
        loss_delay = max(TIME_THRESHOLD * max(self.srtt or INITIAL_RTT, self.latest_rtt), GRANULARITY)
        lost, self.loss_time = [], None
        for pn, p in self.sent.items():
            if pn > self.largest_acked:
                break
            if pn <= self.largest_acked - PKT_THRESHOLD or now - p.time >= loss_delay:
                lost.append(p)
            else:
                t = p.time + loss_delay
                if self.loss_time is None or t < self.loss_time:
                    self.loss_time = t
        if lost:
            self._on_packets_lost(lost, now)

    def _on_packets_lost(self, lost, now: float):
        for p in lost:
            del self.sent[p.pn]
            self.bytes_in_flight -= p.size
            self.n_lost += 1
            self._requeue(p, count_retx=True)
        self.cc.on_congestion(now, max(p.time for p in lost))

    def _requeue(self, p: SentPacket, count_retx=False):
        for f in p.frames:
            if f[0] == "S":
                ss = self.send_streams.get(f[1])
                if ss:
                    ss.on_lost(f[2], f[3], f[4])
                    if count_retx:
                        self.bytes_retx += f[3]
            elif f[0] == "M":
                rs = self.recv_streams.get(f[1])
                if rs:
                    rs.dirty = True

    # ------------------------------------------------------------ send path
    def _schedule_flush(self):
        if not self._flush_scheduled and not self.closed:
            self._flush_scheduled = True
            self.loop.call_soon(self._do_flush)

    def _do_flush(self):
        self._flush_scheduled = False
        self._flush()

    def _has_stream_data(self) -> bool:
        return any(ss.has_data() for ss in self.send_streams.values())

    def _has_data(self) -> bool:
        return (self.ping_pending or any(rs.dirty for rs in self.recv_streams.values())
                or self._has_stream_data())

    def _pacing_rate(self):
        r = self.cc.pacing_rate(self.srtt)
        return r if r else None

    def _flush(self, probes: int = 0):
        if self.closed:
            return
        now = self.loop.time()
        self._pace_wait = False
        while not self.closed:
            window_ok = self.bytes_in_flight < self.cc.cwnd
            pace_ok = now >= self.pacing_next - 1e-4
            if window_ok and not pace_ok:
                self._pace_wait = True
            built = self._build(now, probes > 0 or (window_ok and pace_ok))
            if built is None:
                break
            self._transmit(now, *built)
            probes = max(0, probes - 1)
            now = self.loop.time()
        self._update_timer()

    def _ack_ranges(self):
        return [(a, b - 1) for a, b in reversed(self.recv_ranges.r)][:MAX_ACK_RANGES]

    def _build(self, now: float, allow_data: bool):
        budget = MAX_PAYLOAD
        ack_part = None
        if self.ack_deadline is not None:
            delay = int(max(0.0, now - self.largest_recv_time) * 1e6)
            ack_part = enc_ack(self._ack_ranges(), min(delay, 0xFFFFFFFF))
            budget -= len(ack_part)
        ack_due = self.ack_deadline is not None and now >= self.ack_deadline - 1e-6
        parts, frames, ae = [], [], False
        if allow_data:
            if self.ping_pending:
                parts.append(enc_ping())
                frames.append(("P",))
                budget -= 1
                ae = True
                self.ping_pending = False
            for rs in self.recv_streams.values():
                if rs.dirty and budget >= 13:
                    parts.append(enc_max_stream_data(rs.sid, rs.adv_max))
                    frames.append(("M", rs.sid))
                    budget -= 13
                    rs.dirty = False
                    ae = True
            order = sorted(self.send_streams.values(), key=lambda s: (s.priority, s.served))
            progress = True
            while progress and budget > STREAM_OVERHEAD + 1:
                progress = False
                for ss in order:
                    if budget <= STREAM_OVERHEAD + 1:
                        break
                    fr = ss.next_frame(budget - STREAM_OVERHEAD)
                    if fr is None:
                        continue
                    off, data, fin = fr
                    parts.append(enc_stream(ss.sid, off, data, fin))
                    frames.append(("S", ss.sid, off, len(data), fin))
                    budget -= STREAM_OVERHEAD + len(data)
                    ss.served = next(self._tick)
                    ae = progress = True
        if not parts and not (ack_part is not None and ack_due):
            return None
        if ack_part is not None:
            parts.insert(0, ack_part)
            self.ack_deadline = None
            self.ack_pending_count = 0
        return b"".join(parts), frames, ae

    def _send_packet(self, payload: bytes) -> int:
        if self.next_pn >= (1 << 64) - 1:
            self._terminate("packet number space exhausted")
            return self.next_pn
        pn = self.next_pn
        self.next_pn += 1
        hdr = HDR.pack(PT_DATA, self.peer_cid, pn)
        self.ep.send_datagram(hdr + self.send_cipher.seal(pn, hdr, payload), self.peer_addr)
        self.last_send = self.loop.time()
        return pn

    def _transmit(self, now: float, payload: bytes, frames, ae: bool):
        pn = self._send_packet(payload)
        self.n_sent += 1
        if not ae:
            return                                # ACK-only packets are not tracked / not in flight
        size = HDR_LEN + len(payload) + TAG_LEN
        sp = SentPacket()
        sp.pn, sp.time, sp.size, sp.frames = pn, now, size, frames
        sp.delivered, sp.delivered_time, sp.first_sent = self.delivered, self.delivered_time, self.first_sent_time
        sp.app_limited = not self._has_stream_data()
        self.sent[pn] = sp
        self.bytes_in_flight += size
        self.last_ae_sent = now
        self.cc.on_sent(now, size, self.bytes_in_flight)
        rate = self._pacing_rate()
        if rate:
            self.pacing_next = max(self.pacing_next, now - 0.002) + size / rate

    # ------------------------------------------------------------ timers
    def _pto_interval(self) -> float:
        srtt = self.srtt if self.srtt is not None else INITIAL_RTT
        var = self.rttvar if self.rttvar is not None else INITIAL_RTT / 2
        return (srtt + max(4 * var, GRANULARITY) + MAX_ACK_DELAY) * (2 ** min(self.pto_count, 6))

    def _update_timer(self):
        if self.closed:
            return
        d = [self.last_recv + IDLE_TIMEOUT]
        if self.loss_time is not None:
            d.append(self.loss_time)
        elif self.sent:
            d.append(self.last_ae_sent + self._pto_interval())
        else:
            d.append(self.last_send + KEEPALIVE_INTERVAL)
        if self.ack_deadline is not None:
            d.append(self.ack_deadline)
        if self._pace_wait and self._has_data():
            d.append(self.pacing_next)
        when = min(d)
        if self._timer is not None:
            if abs(self._timer_when - when) < 1e-4:
                return
            self._timer.cancel()
        self._timer_when = when
        self._timer = self.loop.call_at(max(when, self.loop.time()), self._on_timer)

    def _on_timer(self):
        self._timer = self._timer_when = None
        if self.closed:
            return
        now = self.loop.time()
        if now - self.last_recv >= IDLE_TIMEOUT:
            self._terminate("idle timeout")
            return
        probes = 0
        if self.loss_time is not None and now >= self.loss_time - 1e-6:
            self._detect_loss(now)
        elif self.sent and now >= self.last_ae_sent + self._pto_interval() - 1e-6:
            self.pto_count += 1
            for p in list(self.sent.values())[:2]:       # re-send oldest data as a probe
                self._requeue(p)
            if self.pto_count == 3:
                self.cc.on_persistent_congestion(now)
            if not self._has_stream_data():
                self.ping_pending = True
            probes = 2
        if not self.sent and now - self.last_send >= KEEPALIVE_INTERVAL:
            self.ping_pending = True                      # heartbeat
        self._flush(probes)

    def _terminate(self, reason: str):
        if self.closed:
            return
        self.closed, self.close_reason = True, reason
        if self._timer:
            self._timer.cancel()
        self.ep._remove(self)
        for ss in list(self.send_streams.values()):
            if ss.done and not ss.done.done():
                ss.done.set_result(False)
            self._release(ss)
        if self.on_close:
            self.loop.call_soon(self.on_close, self, reason)


# ==================================================================== endpoint
class Endpoint:
    """Owns the raw UDP socket, demultiplexes datagrams to connections, runs the handshake."""

    def __init__(self, loop, bind=("0.0.0.0", 0), identity=None, cc="cubic", sim_loss=0.0, sim_delay=0.0,
                 sim_jitter=0.0, max_conns=512):
        self.loop, self.identity, self.cc = loop, identity, cc
        self.sim_loss, self.sim_delay, self.sim_jitter = sim_loss, sim_delay, sim_jitter
        self.max_conns = max_conns
        self.conns: dict[int, Connection] = {}
        self.pending: dict[tuple, tuple] = {}       # server: (addr, client_cid) -> (conn, cached reply)
        self.on_accept = None
        self._hs = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        for opt in (socket.SO_RCVBUF, socket.SO_SNDBUF):
            try:
                self.sock.setsockopt(socket.SOL_SOCKET, opt, 4 * 1024 * 1024)
            except OSError:
                pass
        self.sock.bind(bind)
        self.addr = self.sock.getsockname()
        loop.add_reader(self.sock.fileno(), self._on_readable)

    # ---- plumbing
    def _new_cid(self) -> int:
        while True:
            c = random.getrandbits(32)
            if c and c not in self.conns:
                return c

    def _on_readable(self):
        for _ in range(512):
            try:
                data, addr = self.sock.recvfrom(2048)
            except (BlockingIOError, InterruptedError):
                return
            except OSError:
                continue                              # e.g. ICMP port-unreachable surfaced on Windows
            try:
                self._dispatch(data, addr)
            except Exception:
                log.exception("error while handling datagram from %s", addr)

    def send_datagram(self, data: bytes, addr):
        if self.sim_loss and random.random() < self.sim_loss:
            return                                    # simulated packet loss
        if self.sim_delay or self.sim_jitter:
            self.loop.call_later(self.sim_delay + random.random() * self.sim_jitter, self._raw_send, data, addr)
        else:
            self._raw_send(data, addr)

    def _raw_send(self, data, addr):
        try:
            self.sock.sendto(data, addr)
        except OSError:
            pass                                      # buffer full / network down: treated as loss

    def _remove(self, conn: Connection):
        self.conns.pop(conn.cid, None)
        key = getattr(conn, "_pending_key", None)
        if key:
            self.pending.pop(key, None)

    def close(self):
        for c in list(self.conns.values()):
            c._terminate("endpoint closed")
        try:
            self.loop.remove_reader(self.sock.fileno())
        except Exception:
            pass
        self.sock.close()

    # ---- demultiplexing
    def _dispatch(self, data: bytes, addr):
        if len(data) < HDR_LEN:
            return
        typ, cid, pn = HDR.unpack_from(data)
        if typ == PT_DATA:
            conn = self.conns.get(cid)
            if conn:
                conn.on_datagram(data[:HDR_LEN], pn, data[HDR_LEN:], addr)
        elif typ == PT_INITIAL and self.identity is not None:
            self._on_initial(data, addr)
        elif typ == PT_HANDSHAKE and self._hs is not None:
            self._on_handshake(data, addr)

    # ---- server side of the handshake
    def _on_initial(self, data: bytes, addr):
        body = data[HDR_LEN:]
        if len(body) != 36:
            return
        ccid, = struct.unpack_from("!I", body)
        cpub = body[4:36]
        key = (addr, ccid)
        ent = self.pending.get(key)
        if ent:                                       # retransmitted Initial -> resend cached reply
            if not ent[0].closed:
                self.send_datagram(ent[1], addr)
            return
        if len(self.conns) >= self.max_conns:
            return
        try:
            spriv, spub = crypto.new_ephemeral()
            scid = self._new_cid()
            k_c2s, k_s2c = crypto.derive_keys(spriv, cpub, cpub, spub)
        except Exception:
            return
        sig = crypto.sign(self.identity, crypto.transcript(cpub, spub, ccid, scid))
        reply = (HDR.pack(PT_HANDSHAKE, ccid, 0) + struct.pack("!I", scid) + spub
                 + crypto.public_bytes(self.identity) + sig)
        conn = Connection(self, False, addr, scid, ccid, k_s2c, k_c2s, self.cc)
        conn._pending_key = key
        self.conns[scid] = conn
        self.pending[key] = (conn, reply)
        self.send_datagram(reply, addr)
        if self.on_accept:
            self.on_accept(conn)

    # ---- client side of the handshake
    async def connect(self, addr, verify=None, timeout: float = 6.0) -> Connection:
        cpriv, cpub = crypto.new_ephemeral()
        ccid = self._new_cid()
        fut = self.loop.create_future()
        self._hs = (ccid, cpriv, cpub, addr, fut, verify)
        pkt = HDR.pack(PT_INITIAL, 0, 0) + struct.pack("!I", ccid) + cpub
        deadline, delay = self.loop.time() + timeout, 0.25
        try:
            while True:
                self.send_datagram(pkt, addr)
                remaining = deadline - self.loop.time()
                if remaining <= 0:
                    raise ConnectionError("handshake timeout: server unreachable")
                try:
                    return await asyncio.wait_for(asyncio.shield(fut), min(delay, remaining))
                except asyncio.TimeoutError:
                    delay = min(delay * 2, 1.0)
        finally:
            self._hs = None

    def _on_handshake(self, data: bytes, addr):
        ccid, cpriv, cpub, _haddr, fut, verify = self._hs
        _, cid, _ = HDR.unpack_from(data)
        body = data[HDR_LEN:]
        if cid != ccid or fut.done() or len(body) != 4 + 32 + 32 + 64:
            return
        scid, = struct.unpack_from("!I", body)
        spub, static, sig = body[4:36], body[36:68], body[68:132]
        try:
            if not crypto.verify(static, sig, crypto.transcript(cpub, spub, ccid, scid)):
                raise ConnectionError("server signature invalid")
            if verify:
                verify(static)
            k_c2s, k_s2c = crypto.derive_keys(cpriv, spub, cpub, spub)
        except Exception as exc:
            fut.set_exception(exc if isinstance(exc, ConnectionError) else ConnectionError(str(exc)))
            return
        conn = Connection(self, True, addr, ccid, scid, k_c2s, k_s2c, self.cc)
        self.conns[ccid] = conn
        fut.set_result(conn)
