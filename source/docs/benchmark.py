"""Benchmark: CUBIC vs BBR goodput for a 2 MB transfer, 20 ms RTT, several loss rates."""
import asyncio, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.test_transport import Pair

async def run(cc, loss, size=2_000_000):
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
    res = []
    for loss in (0.0, 0.01, 0.03, 0.05):
        for cc in ("cubic", "bbr"):
            r = await run(cc, loss); res.append(r); print(r, flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(__file__), "benchmark.json"), "w"), indent=1)
asyncio.run(main())
