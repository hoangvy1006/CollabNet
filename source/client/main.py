"""Client CollabNet: lõi mạng + cổng HTTP cục bộ phục vụ UI trên trình duyệt.

Chạy:  python -m client.main --ui-port 8080
Rồi mở http://127.0.0.1:8080 trên trình duyệt.

Mỗi tiến trình = một người dùng, có thư mục trạng thái riêng (`client_state_<ui-port>`) chứa file đã nhận,
khoá server đã ghim và khoá P2P của client.
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
    """Khởi động ClientCore + Gateway rồi chạy cho tới khi tiến trình bị dừng (Ctrl+C)."""
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
    """Phân tích tham số dòng lệnh, cấu hình log rồi chạy vòng lặp asyncio của client."""
    ap = argparse.ArgumentParser(description="CollabNet client")
    ap.add_argument("--ui-host", default="127.0.0.1")
    ap.add_argument("--ui-port", type=int, default=8080)
    ap.add_argument("--server", default="127.0.0.1:9000", help="host:port mặc định hiện trong form đăng nhập")
    ap.add_argument("--state-dir", default=None, help="thư mục file nhận + khoá server đã ghim (mặc định ./client_state_<cổng>)")
    ap.add_argument("--cc", choices=["cubic", "bbr"], default="cubic")
    ap.add_argument("--open", action="store_true", help="tự mở trình duyệt")
    ap.add_argument("--sim-loss", type=float, default=0.0, help="tỉ lệ mất gói mô phỏng (để kiểm thử)")
    ap.add_argument("--sim-delay-ms", type=float, default=0.0, help="độ trễ một chiều mô phỏng, ms (để kiểm thử)")
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
