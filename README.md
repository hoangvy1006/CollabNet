# CollabNet — Distributed Streaming-based Client-Server Collaboration Application

Chat (broadcast + riêng), danh sách người dùng online, truyền file tin cậy, chạy trên **UDP thuần**
với transport tự viết (đa stream kiểu QUIC, sliding window, ACK/SACK, retransmit chọn lọc, CUBIC/BBR)
và mã hoá AES-256-GCM. UI là web (HTML + JavaScript phía client) phục vụ bởi một HTTP server tự viết.

## 1. Yêu cầu
* Python **3.10+** (đã thử 3.12), Windows / macOS / Linux
* Một thư viện ngoài duy nhất: `cryptography` (AES-GCM, X25519, Ed25519)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install cryptography           # hoặc: pip install -r requirements.txt
```

## 2. Chạy server (Terminal 1)
```bash
python -m server.server --port 9000
```
Server in ra *fingerprint* khoá định danh Ed25519. Dữ liệu (users.json, khoá server) nằm trong `./server_data`.
Tuỳ chọn: `--cc cubic|bbr`, `--host`, `--data-dir`, `--max-file-mb`, `--no-beacon`.

## 3. Chạy client (mỗi người dùng một terminal)
```bash
python -m client.main --ui-port 8080 --server 127.0.0.1:9000 --open
python -m client.main --ui-port 8081 --server 127.0.0.1:9000 --open    # người dùng thứ 2 (cùng máy)
python -m client.main --ui-port 8082 --server 127.0.0.1:9000 --open    # người dùng thứ 3 (cùng máy)
... # người dùng thứ n (cùng máy)
```
Mở `http://127.0.0.1:8080`, nhập tên + mật khẩu (tên mới sẽ tự đăng ký, mật khẩu ≥ 4 ký tự).
Khác máy: dùng IP của server (`--server 192.168.1.10:9000`) hoặc nút **"Tìm trong LAN"** (server broadcast beacon UDP).
Mỗi client lưu file nhận và khoá server đã ghim trong `./client_state_<ui-port>/`.

Cách dùng UI: chọn *Mọi người* để chat chung, chọn một người để nhắn riêng; nút 📎 hoặc kéo-thả để gửi file
(chỉ gửi cho một người). Thanh trên cùng hiển thị thuật toán CC, RTT, cwnd, gói mất theo thời gian thực.

> Lần đầu kết nối, client ghim (TOFU) fingerprint của server. Nếu khoá đổi, client **từ chối** kết nối (chống MITM).
> Muốn tin khoá mới: xoá mục tương ứng trong `known_hosts.json`.

## 4. Mô phỏng mạng xấu (kiểm thử)
```bash
python -m server.server --port 9000 --cc bbr --sim-loss 0.05 --sim-delay-ms 20
python -m client.main --ui-port 8080 --cc bbr --sim-loss 0.05 --sim-delay-ms 20
```

## 5. Kiểm thử tự động
```bash
python -m unittest discover -s tests -t . -v        # 19 test, ~45 giây
python docs/benchmark.py                            # CUBIC vs BBR
python docs/build_report.py                         # sinh lại docs/report.pdf (cần reportlab, matplotlib)
```

## 6. Cấu trúc mã nguồn
```
common/transport.py   Connection + Endpoint: stream, ACK/SACK, loss recovery, flow control, handshake
common/congestion.py  CUBIC và BBR + pacing          common/crypto.py   X25519/Ed25519/HKDF/AES-GCM/PBKDF2
common/packet.py      định dạng gói + frame          common/protocol.py thông điệp ứng dụng (JSON có độ dài)
common/discovery.py   beacon broadcast / dò server   server/server.py   xác thực, presence, định tuyến, relay file
client/core.py        logic mạng phía client         client/gateway.py  HTTP/SSE server tự viết (raw TCP)
client/web/           UI (index.html, app.js, style.css)      tests/  docs/report.pdf
```

## 7. Đối chiếu yêu cầu đề bài
| Bước | Nội dung | Vị trí |
|---|---|---|
| 1 | Thiết kế giao thức, state diagram | `docs/report.pdf` mục 2, `common/packet.py`, `common/protocol.py` |
| 2 | Handshake client-server + ACK | `Endpoint.connect/_on_initial` (INITIAL/HANDSHAKE), AUTH_OK |
| 3 | Xác thực & quản lý trạng thái (user, IP, port) | `server/server.py` (`Session`, `PEERS`) |
| 4 | Đồng thời (async I/O) | asyncio + `add_reader` trên socket UDP thô; nhiều client cùng lúc |
| 5 | Streaming nhạy thời gian: định tuyến tin nhắn | mỗi tin một stream, broadcast/unicast (`_route_msg`), chống HoL |
| 6 | Truyền file tin cậy, chia chunk, ghép lại trên UDP | `SendStream/RecvStream`, `FILE/FILE_END` + SHA-256 |
| 7 | Chịu lỗi: timeout, ngắt kết nối, thoát êm | PTO/idle/keep-alive, auto-reconnect, CLOSE |
| 8 | Mã hoá payload | AES-256-GCM từng gói, X25519 + chữ ký Ed25519 |
| 9 | UI HTTP + JS phía client | `client/web`, tiến trình file, danh sách online |
| 10 | Kiểm thử & chất lượng mã | `tests/` (19 test), mô phỏng mất gói/trễ |
