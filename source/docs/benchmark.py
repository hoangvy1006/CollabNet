"""Benchmark: CUBIC vs BBR goodput for a 2 MB transfer, 20 ms RTT, several loss rates.

Chạy từ thư mục gốc dự án: ``python docs/benchmark.py``.
Kết quả được ghi đè vào ``docs/benchmark.json`` (số liệu dùng cho báo cáo).
"""
import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.test_transport import Pair


async def run(cc, loss, size=2_000_000):
    """Đo thời gian truyền `size` byte qua một cặp client/server có mất gói và trễ 20 ms.

    Trả về dict gồm thời gian, goodput (Mbps) và số gói bị coi là mất do thuật toán điều khiển tắc nghẽn.
    """
    p = await Pair(cc, loss, 0.01).start()
    try:
        sid = p.client.open_stream(1)
        t0 = time.monotonic()
        p.client.send(sid, os.urandom(size), fin=True)
        await p.wait_fin(sid, 120)
        dt = time.monotonic() - t0
        return {"cc": cc, "loss": loss, "seconds": round(dt, 2), "mbps": round(size * 8 / dt / 1e6, 2),
                "lost": p.client.stats()["lost_pkts"]}
    finally:
        p.close()


async def main():
    # Mỗi mức mất gói chạy cả hai thuật toán để so sánh trực tiếp (cùng một link mô phỏng).
    res = []
    for loss in (0.0, 0.01, 0.03, 0.05):
        for cc in ("cubic", "bbr"):
            r = await run(cc, loss)
            res.append(r)
            print(r, flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(__file__), "benchmark.json"), "w"), indent=1)


if __name__ == "__main__":
    asyncio.run(main())
