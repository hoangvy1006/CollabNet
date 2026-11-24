# Bộ lọc Wireshark cho buổi demo CollabNet

Dán trực tiếp các biểu thức dưới đây vào thanh **Apply a display filter** (Ctrl + /).
Mỗi mục là một "màn" riêng để trình bày tuần tự trước lớp.

## 0. Bản đồ cổng của chương trình (dùng để đặt filter)

| Thành phần | Giao thức / cổng | Ghi chú |
|---|---|---|
| Server CollabNet | TCP **9000** | bắt tay TCP: HELLO → HELLO_ACK (rồi đóng) |
| Server CollabNet | UDP **9000** | bắt tay mã hoá, AUTH, MSG, PEERS, HISTORY, ACK |
| Beacon tìm server trong LAN | UDP **9998** | broadcast `255.255.255.255` |
| P2P truyền file (client ↔ client) | UDP **cổng ngẫu nhiên** (bind `0.0.0.0:0`) | không đi qua server |
| UI web của mỗi client | TCP **8080, 8081, 8082…** | HTTP thô + SSE `/api/events` |

Cấu trúc 1 datagram CollabNet (để giải thích trên slide):

```
payload[0]    : loại gói   0x01 = INITIAL (client chào)
                           0x02 = HANDSHAKE (server chào + chữ ký Ed25519)
                           0x10 = DATA (đã mã hoá AES-256-GCM)
payload[1..4] : connection id
payload[5..12]: packet number (số thứ tự gói, 8 byte)
payload[13..] : frame đã mã hoá (STREAM/ACK/PING/CLOSE…) + 16 byte GCM tag
```

---

## 1. Toàn cảnh buổi demo (mở đầu)

```
udp.port == 9000 || udp.port == 9998 || tcp.port == 9000 || (tcp.port >= 8080 && tcp.port <= 8099)
```

Bỏ nhiễu của máy (ARP, IPv6 neighbor discovery, DNS…):

```
(udp.port == 9000 || udp.port == 9998 || tcp.port == 9000 || (tcp.port >= 8080 && tcp.port <= 8099)) && !(arp || icmp || icmpv6 || dns)
```

## 2. Bắt tay transport (X25519 + Ed25519) — Bước 2 của đề bài

Client gửi `INITIAL`:

```
udp.payload[0] == 0x01
```

Server trả `HANDSHAKE`:

```
udp.payload[0] == 0x02
```

Chỉ bắt tay với server (bỏ qua bắt tay P2P):

```
(udp.payload[0] == 0x01 || udp.payload[0] == 0x02) && udp.port == 9000
```

Bắt tay P2P trước khi truyền file:

```
(udp.payload[0] == 0x01 || udp.payload[0] == 0x02) && udp.port != 9000 && udp.port != 9998
```

> Gói INITIAL được gửi lại mỗi 0,25 s → 1 s cho tới khi có HANDSHAKE, nên thấy
> nhiều gói `0x01` giống nhau là bình thường (chống mất gói).

## 3. Đăng nhập / đăng ký

Phần lõi (AUTH / AUTH_OK / AUTH_FAIL) **đã mã hoá**, chỉ thấy dòng gói UDP:

```
udp.payload[0] == 0x10 && udp.port == 9000
```

Bản rõ của thao tác đăng nhập nằm ở HTTP giữa trình duyệt và client (cổng UI):

```
http.request.method == "POST" && http.request.uri == "/api/login"
```

Xem nội dung: bấm gói → `JavaScript Object Notation: application/json` (có `user`, `pass`, `server`).
Dùng luôn cho đăng xuất:

```
http.request.method == "POST" && (http.request.uri == "/api/login" || http.request.uri == "/api/logout")
```

## 4. Gửi tin nhắn chat

Toàn bộ dữ liệu ứng dụng đi qua server (mỗi tin là **một stream riêng**):

```
udp.payload[0] == 0x10 && udp.port == 9000
```

Tin nhắn là các gói nhỏ, xen với ACK:

```
udp.payload[0] == 0x10 && udp.port == 9000 && udp.length < 200
```

Tách riêng một tin để "Follow UDP stream":

```
udp.payload[0] == 0x10 && udp.port == 9000 && ip.addr == 127.0.0.1
```
(chọn 1 gói → chuột phải → **Follow → UDP Stream**; sau đó lọc `udp.stream eq <số>`)

Bản rõ nội dung tin nhắn (REST của UI):

```
http.request.method == "POST" && http.request.uri == "/api/send"
```

## 5. Truyền file (P2P, không qua server)

Toàn bộ luồng file giữa hai client (cổng ngẫu nhiên, khác 9000/9998):

```
udp.payload[0] == 0x10 && udp.port != 9000 && udp.port != 9998
```

Chỉ các gói chở dữ liệu file (gần đầy MTU ~1200 B), bỏ ACK/PING:

```
udp.port != 9000 && udp.port != 9998 && udp.length > 1000
```

Ngược lại, chỉ ACK/keep-alive (gói rỗng):

```
udp.port != 9000 && udp.port != 9998 && udp.length < 80
```

Phía UI: chọn file để gửi và tải file về

```
http.request.method == "POST" && http.request.uri == "/api/upload"
http.request.uri contains "/api/download/"
```

Thống kê nhanh để chứng minh "chia chunk + ghép lại": **Statistics → Conversations → UDP**,
cột Packets/Bytes của cặp cổng P2P chính là số chunk đã trao đổi.

## 6. ACK, mất gói, keep-alive (Bước 7 của đề bài)

Gói nhỏ trên đường tới server = ACK / PING:

```
udp.payload[0] == 0x10 && udp.port == 9000 && udp.length < 80
```

Đếm gói theo chiều (dùng **Statistics → Endpoints**, hoặc cột tuỳ biến bên dưới).

Mô phỏng mạng xấu rồi quan sát gửi lại:

```bash
python -m server.server --port 9000 --sim-loss 0.05 --sim-delay-ms 20
python -m client.main --ui-port 8080 --sim-loss 0.05 --sim-delay-ms 20
```

```
udp.port == 9000 && udp.payload[0] == 0x10
```
→ bật **View → Time Display Format → Seconds Since Previous Displayed Packet**, các gói
cách nhau ~PTO là gói gửi lại.

## 7. Presence / tìm server trong LAN

Beacon của server:

```
udp.port == 9998
```

Chỉ beacon broadcast:

```
udp.port == 9998 && ip.dst == 255.255.255.255
```

## 8. Tầng UI (HTTP + SSE) — Bước 9 của đề bài

Tất cả lưu lượng web của các client:

```
tcp.port >= 8080 && tcp.port <= 8099
```

Bắt tay TCP của trình duyệt:

```
tcp.flags.syn == 1 && tcp.flags.ack == 0 && tcp.port >= 8080 && tcp.port <= 8099
```

Danh sách request:

```
http.request && tcp.port >= 8080 && tcp.port <= 8099
```

Kênh đẩy sự kiện thời gian thực (Server-Sent Events):

```
http.request.uri == "/api/events"
```
(chọn request → **Follow → TCP Stream** để thấy các dòng `data: {...}`)

---

## 9. Cột tuỳ biến cho dễ nhìn (nên làm trước khi demo)

Chuột phải tiêu đề cột → **Column Preferences…** → dấu `+`:

| Tiêu đề | Loại | Field / công thức |
|---|---|---|
| Kind | Custom | `udp.payload[0]` |
| PN | Custom | `udp.payload[5:8]` |
| CID | Custom | `udp.payload[1:4]` |

Như vậy bảng gói hiện ngay `1` (INITIAL), `2` (HANDSHAKE), `16` (DATA) và số thứ tự gói,
rất tiện nói "gói số 105 bị mất nên số 106–108 được gửi lại".

## 10. Coloring rules gợi ý (View → Coloring Rules)

| Filter | Màu | Ý nghĩa |
|---|---|---|
| `udp.payload[0] == 0x01` | xanh dương nhạt | INITIAL |
| `udp.payload[0] == 0x02` | xanh lá nhạt | HANDSHAKE |
| `udp.port == 9998` | xám | beacon LAN |
| `http.request` | vàng | thao tác UI |
| `udp.length > 1000 && udp.port != 9000` | cam | chunk file P2P |

## 11. Capture filter (ô "Capture filter", hoặc `tshark -f`)

Chỉ bắt lưu lượng của ứng dụng (nhẹ file, dễ nhìn):

```
udp port 9000 or udp port 9998 or tcp portrange 8080-8099
```

Chỉ bắt một máy khác trong LAN:

```
host 192.168.1.10 and (udp or tcp portrange 8080-8099)
```

Chỉ bắt phần P2P (file) khi đã biết cổng: lấy cổng P2P trong `PEERS`/log, rồi:

```
udp port 54321
```

## 12. Lệnh tshark theo từng "cảnh" demo (tuỳ chọn)

Chạy song song với Wireshark để có file `.pcapng` nộp kèm báo cáo.
Thay `"Wi-Fi"` bằng tên card đang dùng (`tshark -D` để liệt kê; demo cùng máy thì
dùng card **Adapter for loopback traffic capture**).

```bash
# cảnh 1: bắt tay + đăng nhập
tshark -i "Wi-Fi" -f "udp port 9000" -a duration:20 -w handshake_login.pcapng

# cảnh 2: gửi vài tin nhắn chat
tshark -i "Wi-Fi" -f "udp port 9000" -a duration:20 -w chat.pcapng

# cảnh 3: gửi file P2P (bắt mọi UDP để không sót cổng ngẫu nhiên)
tshark -i "Wi-Fi" -f "udp" -a duration:30 -w file_p2p.pcapng

# cảnh 4: UI web + SSE
tshark -i "Wi-Fi" -f "tcp portrange 8080-8099" -a duration:20 -w ui_http.pcapng
```

Lọc lại file đã bắt (giữ đúng các gói cần trình bày):

```bash
tshark -r file_p2p.pcapng -Y "udp.port != 9000 && udp.port != 9998" -w file_only.pcapng
tshark -r handshake_login.pcapng -Y "udp.payload[0] == 0x01 || udp.payload[0] == 0x02" -w handshake_only.pcapng
```

Đọc nhanh trên terminal (không cần mở GUI):

```bash
tshark -r chat.pcapng -Y "udp.payload[0] == 0x10 && udp.port == 9000" -T fields -e frame.number -e ip.src -e ip.dst -e udp.length
```

---

## 13. Lưu ý khi trình bày (rất nên nói trước lớp)

1. **Không đọc được nội dung tin nhắn trong Wireshark** — đó chính là điểm cộng của đồ án:
   mỗi gói bị AES-256-GCM mã hoá, khoá sinh từ X25519 trong bắt tay và ký bằng Ed25519.
   Wireshark chỉ thấy loại gói, connection id, số thứ tự và kích thước.
   Muốn khoe nội dung thì chiếu phần HTTP `/api/send` (bản rõ trong máy) hoặc log của ứng dụng.
2. Khi chiếu `/api/login`, mật khẩu hiện rõ trong HTTP → nhắc rằng đây là kênh nội bộ
   `127.0.0.1`, còn trên đường truyền thật (UDP) mật khẩu nằm trong AUTH đã mã hoá.
3. Demo **cùng một máy** thì mọi gói nằm trên card loopback: trong Wireshark phải chọn
   *Adapter for loopback traffic capture* (Windows cần Npcap) thì mới thấy.
   Demo **hai máy trong LAN** thì bắt trên Wi-Fi/Ethernet và thấy đúng địa chỉ IP thật.
4. Công thức dùng ở đây là `udp.payload[0]` (byte đầu của payload UDP), **không phải**
   `udp[8]`: phần payload UDP là buffer riêng nên `udp[8]` không khớp gói nào (đã thử bằng
   tshark trên lưu lượng thật). Tương tự: connection id = `udp.payload[1:4]`, packet number
   = `udp.payload[5:8]`. Công thức đúng cho cả IPv4 và IPv6.
