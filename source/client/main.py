"""CollabNet client: network core + local HTTP gateway serving the browser UI.

Run:  python -m client.main --ui-port 8080
Then open http://127.0.0.1:8080 in a browser.

Tiếng Việt: điểm khởi chạy client. Mỗi tiến trình = một người dùng, có thư mục trạng thái riêng
(`client_state_<ui-port>`) chứa file đã nhận và khoá server đã ghim.
"""
import argparse
import asyncio
import logging
import os
import sys
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.core import ClientCore
from client.gateway import Gateway


async def amain(args):
    loop = asyncio.get_running_loop()
    state = args.state_dir or f"./client_state_{args.ui_port}"
    core = ClientCore(loop, state, args.cc, args.sim_loss, args.sim_delay_ms / 1000)
    gw = Gateway(core, args.ui_host, args.ui_port, args.server)
    await gw.start()
    url = f"http://{args.ui_host}:{gw.port}"
    print(f"CollabNet client UI: {url}   (state dir: {state}, congestion control: {args.cc})")
    if args.open:
        webbrowser.open(url)
    try:
        await asyncio.Event().wait()
    finally:
        await core.logout()
        gw.close()


def main():
    ap = argparse.ArgumentParser(description="CollabNet client")
    ap.add_argument("--ui-host", default="127.0.0.1")
    ap.add_argument("--ui-port", type=int, default=8080)
    ap.add_argument("--server", default="127.0.0.1:9000", help="default host:port shown in the login form")
    ap.add_argument("--state-dir", default=None, help="downloads + pinned server keys (default ./client_state_<port>)")
    ap.add_argument("--cc", choices=["cubic", "bbr"], default="cubic")
    ap.add_argument("--open", action="store_true", help="open the browser automatically")
    ap.add_argument("--sim-loss", type=float, default=0.0, help="simulated packet loss probability (testing)")
    ap.add_argument("--sim-delay-ms", type=float, default=0.0, help="simulated one-way delay (testing)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(amain(args))
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
