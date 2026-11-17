"""Đặt lại dữ liệu server CollabNet: xoá toàn bộ tài khoản và lịch sử chat.

Dùng trước buổi kiểm thử với giảng viên để server trở về trạng thái sạch: không còn tài khoản nào
(lần đăng nhập kế tiếp sẽ đăng ký mới) và không còn tin nhắn cũ nào được gửi lại cho client.

Chạy trong thư mục ``source/``:

    python -m server.reset                 # xoá users + lịch sử trong ./server_data
    python -m server.reset --dry-run       # chỉ xem sẽ xoá gì
    python -m server.reset -y              # không hỏi xác nhận

Mặc định KHÔNG xoá ``server_identity.key``: giữ nguyên fingerprint để các client đã pin server vẫn kết nối
được. Thêm ``--with-identity`` nếu muốn đổi luôn khoá của server (khi đó client phải xoá ``known_hosts.json``
trong thư mục trạng thái của nó, nếu không sẽ bị từ chối vì fingerprint lạ).

Phải TẮT server VÀ tất cả client trước khi chạy:
  * server đang chạy vẫn giữ users/lịch sử trong RAM và sẽ ghi đè lại file ngay sau đó;
  * client còn mở vẫn giữ phiên đăng nhập cũ, nên khi thấy server "quên" tài khoản nó sẽ tự đăng nhập lại và
    tạo lại user chỉ trong vài giây.
Vì vậy script tự kiểm tra cổng UDP của server và các cổng UI của client (mặc định 8080, 8081 — đổi bằng
``--ui-ports``), rồi từ chối chạy nếu còn cổng bận. ``--force`` để bỏ qua khi chắc chắn cổng đó không phải CollabNet.
"""
import argparse
import json
import os
import socket

# Các file thuộc về tài khoản người dùng; xoá đi là server quay về trạng thái như lần chạy đầu.
TARGETS = ("users.json", "first_seen.json", "history.json")
IDENTITY = "server_identity.key"


def _load_json(path):
    """Đọc file JSON, trả về None nếu file không có hoặc hỏng (chỉ dùng để đếm cho phần tóm tắt)."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _counts(data_dir):
    """Số tài khoản và số tin nhắn đang lưu, để in ra trước khi xoá."""
    users = _load_json(os.path.join(data_dir, "users.json"))
    history = _load_json(os.path.join(data_dir, "history.json"))
    return (len(users) if isinstance(users, dict) else 0,
            len(history) if isinstance(history, list) else 0)


def _port_busy(port, host="0.0.0.0", kind=socket.SOCK_DGRAM):
    """True nếu bind được thất bại, tức cổng đã có tiến trình khác dùng (server UDP hoặc gateway HTTP của client)."""
    sock = socket.socket(socket.AF_INET, kind)
    try:
        sock.bind((host, port))
        return False
    except OSError:
        return True
    finally:
        sock.close()


def _parse_ports(text):
    """Đọc danh sách cổng dạng "8080,8081"; bỏ qua phần không phải số."""
    ports = []
    for part in str(text).replace(";", ",").split(","):
        part = part.strip()
        if part.isdigit():
            ports.append(int(part))
    return ports


def main(argv=None) -> int:
    """Phân tích tham số, xác nhận với người dùng rồi xoá các file dữ liệu; trả về mã thoát."""
    ap = argparse.ArgumentParser(description="Xoá toàn bộ tài khoản và lịch sử chat của server CollabNet")
    ap.add_argument("--data-dir", default="./server_data", help="thư mục dữ liệu của server (mặc định ./server_data)")
    ap.add_argument("--port", type=int, default=9000, help="cổng UDP của server, dùng để phát hiện server còn chạy")
    ap.add_argument("--ui-ports", default="8080,8081",
                    help="các cổng UI của client cần kiểm tra, cách nhau bằng dấu phẩy (mặc định 8080,8081)")
    ap.add_argument("--with-identity", action="store_true",
                    help="xoá cả server_identity.key (đổi fingerprint của server)")
    ap.add_argument("--dry-run", action="store_true", help="chỉ in ra sẽ xoá gì, không xoá thật")
    ap.add_argument("-y", "--yes", action="store_true", help="không hỏi xác nhận")
    ap.add_argument("--force", action="store_true",
                    help="vẫn chạy dù cổng server/client còn bận (khi chắc chắn đó không phải CollabNet)")
    args = ap.parse_args(argv)

    data_dir = os.path.abspath(args.data_dir)
    if not os.path.isdir(data_dir):
        print(f"Không thấy thư mục dữ liệu: {data_dir}")
        return 1

    files = [os.path.join(data_dir, name) for name in TARGETS]
    if args.with_identity:
        files.append(os.path.join(data_dir, IDENTITY))
    present = [path for path in files if os.path.exists(path)]
    n_users, n_messages = _counts(data_dir)

    print(f"Thư mục dữ liệu : {data_dir}")
    print(f"Tài khoản       : {n_users}")
    print(f"Tin nhắn        : {n_messages}")
    print("Sẽ xoá          : " + (", ".join(os.path.basename(p) for p in present) or "(không có gì)"))
    if args.with_identity:
        print("CẢNH BÁO: xoá server_identity.key -> fingerprint đổi, client phải xoá known_hosts.json.")

    if not present:
        print("\nServer đã sạch, không cần làm gì.")
        return 0

    # Server bind UDP 0.0.0.0, gateway của client bind TCP 127.0.0.1 -> kiểm tra đúng giao thức/địa chỉ từng loại.
    problems = []
    if _port_busy(args.port, "0.0.0.0", socket.SOCK_DGRAM):
        problems.append(f"Cổng UDP {args.port} đang bận -> có thể server vẫn chạy.")
    busy_ui = [port for port in _parse_ports(args.ui_ports)
               if _port_busy(port, "127.0.0.1", socket.SOCK_STREAM)]
    if busy_ui:
        problems.append("Cổng UI " + ", ".join(str(p) for p in busy_ui) + " đang bận -> có thể client vẫn đang mở; "
                        "client còn phiên sẽ tự đăng nhập lại và tạo lại tài khoản ngay sau khi reset.")
    if problems:
        print()
        for line in problems:
            print(line)

    if args.dry_run:
        print("\n--dry-run: không xoá gì.")
        return 0

    if problems and not args.force:
        print("Hãy tắt server và các client (Ctrl+C) rồi chạy lại. "
              "Nếu chắc chắn các cổng đó không thuộc CollabNet, thêm --force.")
        return 2

    if not args.yes:
        try:
            answer = input("\nXoá các file trên? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes", "có", "co"):
            print("Đã huỷ.")
            return 1

    for path in present:
        try:
            os.remove(path)
        except OSError as exc:
            print(f"không xoá được {os.path.basename(path)}: {exc}")
            return 1
        print(f"đã xoá {os.path.basename(path)}")

    print("\nXong: server không còn tài khoản và lịch sử chat. Khởi động lại server là dùng được ngay.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
