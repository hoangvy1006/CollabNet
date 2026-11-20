# KỊCH BẢN THUYẾT TRÌNH & DEMO — CollabNet

**Đồ án:** Assignment 1 — Distributed and Streaming-based Client-Server Collaboration Application

**Thời lượng khuyến nghị:** 18–20 phút (10 bước, mỗi bước khoảng 1,5 phút)

**Đối tượng người đọc:** người chưa từng dùng Wireshark vẫn có thể cầm tài liệu này đọc và thao tác theo.

> **Cách dùng tài liệu này.** Mỗi bước có đúng 4 phần: (1) lời thuyết trình đọc gần như nguyên văn,
> (2) các thao tác bấm trên web, (3) filter + cách tìm gói + ý nghĩa gói trong Wireshark,
> (4) câu hỏi giảng viên hay hỏi. Những câu trong khung “NÓI” là lời nói trực tiếp; những câu trong
> khung “BẤM” là thao tác tay. Không cần hiểu hết kỹ thuật, chỉ cần làm đúng thứ tự.

---

## 0. TRƯỚC KHI VÀO PHÒNG THI

### 0.1. Cần có trên máy

| Thứ cần có | Kiểm tra bằng cách | Nếu thiếu |
|---|---|---|
| Python 3.10+ | `python --version` | Cài Python từ python.org, nhớ tick “Add Python to PATH” |
| Thư viện `cryptography` | `python -c "import cryptography; print(cryptography.__version__)"` | `pip install cryptography` |
| Wireshark 4.x + Npcap | Mở Wireshark, thấy card “Adapter for loopback traffic capture” | Cài lại Wireshark, tick “Install Npcap”, tick “Support loopback traffic” |
| 3 tab trình duyệt | Mở được `http://127.0.0.1:8080` | Dùng Chrome/Edge/Firefox bất kỳ |

**Lưu ý quan trọng về Npcap:** demo chạy 3 client trên cùng một máy nên mọi gói đi qua card loopback.
Nếu trong danh sách card của Wireshark không có “Adapter for loopback traffic capture”, hãy cài lại Npcap
(tải ở npcap.com) và tick ô **Support loopback traffic**. Không có card này thì **không bắt được gói nào**,
dù ứng dụng vẫn chạy bình thường.

### 0.2. Sơ đồ cổng — thuộc lòng 4 dòng này

| Thành phần | Giao thức / cổng | Nhìn thấy gì trong Wireshark |
|---|---|---|
| Server CollabNet | UDP **9000** | Đăng nhập, chat, presence, lịch sử, ACK |
| Beacon tìm server trong LAN | UDP **9998** | Gói broadcast JSON 2 giây một lần |
| Truyền file P2P (client ↔ client) | UDP **cổng ngẫu nhiên** | Các gói ~1200 byte, **không** đi qua 9000 |
| Giao diện web của mỗi client | TCP **8080, 8081, 8082** | HTTP thô + SSE `/api/events` |

Câu thần chú khi giảng viên hỏi “file đi đường nào?”:
**“Chat và đăng nhập đi qua UDP 9000; file đi thẳng P2P trên cổng ngẫu nhiên, server chỉ giới thiệu peer.”**

### 0.3. Khởi động trong 5 lệnh (cách nhanh nhất)

Mở **Command Prompt** (không phải Git Bash) và dán từng dòng. Thay đường dẫn bằng đường dẫn thật trên máy.

```bat
cd /d "C:\Users\hvy14\Documents\Mạng Máy Tính\Assignment\ASS1\source"

REM 1) Xoá dữ liệu cũ để buổi demo sạch (server và client phải đang tắt)
..\.venv\Scripts\python.exe -m server.reset -y

REM 2) Mở server ở cửa sổ riêng
start "CollabNet server" cmd /k ..\.venv\Scripts\python.exe -m server.server --port 9000

REM 3) Mở 3 client ở 3 cửa sổ riêng, mỗi client một cổng UI
start "Client 8080" cmd /k ..\.venv\Scripts\python.exe -m client.main --ui-port 8080 --server 127.0.0.1:9000 --open
start "Client 8081" cmd /k ..\.venv\Scripts\python.exe -m client.main --ui-port 8081 --server 127.0.0.1:9000 --open
start "Client 8082" cmd /k ..\.venv\Scripts\python.exe -m client.main --ui-port 8082 --server 127.0.0.1:9000 --open
```

Nếu không dùng `start`, mở 4 cửa sổ Command Prompt và chạy 4 lệnh `..\.venv\Scripts\python.exe -m ...`
tương ứng ở trên. **Không tắt 4 cửa sổ này trong suốt buổi demo.**

Kiểm tra nhanh: 3 tab trình duyệt tự mở ra. Nếu chưa mở, tự mở
`http://127.0.0.1:8080`, `http://127.0.0.1:8081`, `http://127.0.0.1:8082`.

### 0.4. Đăng nhập 3 người dùng (làm một lần, dùng cho cả buổi)

| Tab | Tên người dùng | Mật khẩu | Vai |
|---|---|---|---|
| 8080 | `alice` | `1234` | Người gửi chính, demo chat/file |
| 8081 | `bob` | `1234` | **User1** — người sẽ đăng xuất và nhận lại tin/file |
| 8082 | `carol` | `1234` | Người quan sát, chứng minh chat riêng không lộ |

Tên chưa tồn tại sẽ **tự đăng ký** ngay lần đăng nhập đầu. Nếu quên mật khẩu cũ, chạy lại
`server.reset -y` khi đã tắt server + client rồi làm lại.

**Mẹo tạo cuộc trò chuyện riêng trước khi Bob đăng xuất:** ở tab Alice, bấm `bob` trong cột trái,
gửi một tin “Chào Bob”. Ở tab Bob, trả lời “Chào Alice”. Việc này để sau khi Bob đăng xuất, dòng `bob`
vẫn còn trong danh sách của Alice với nhãn **Offline** — khi đó mới bấm vào để gửi tiếp được.
Nếu chưa từng chat riêng, Bob sẽ biến mất khỏi danh sách khi offline (đây là hành vi có chủ ý:
danh sách chỉ hiện người đang online và những cuộc trò chuyện đã có).

### 0.5. Bố cục màn hình khi trình bày

Đặt 4 cửa sổ cạnh nhau theo thứ tự:

| Vị trí | Cửa sổ | Vai |
|---|---|---|
| Trái, rộng nhất | Wireshark | Bắt gói và chiếu filter |
| Giữa | Server console | Log đăng nhập, đóng kết nối |
| Phải, trên | Alice — `http://127.0.0.1:8080` | Người gửi chính |
| Phải, giữa | Bob — `http://127.0.0.1:8081` | User1 — người sẽ đăng xuất |
| Phải, dưới | Carol — `http://127.0.0.1:8082` | Người quan sát |

Khi nói về Wireshark, dùng chuột chỉ vào **thanh filter xanh** ở trên cùng. Khi nói về web, chỉ vào tab
tương ứng. Đừng vừa nói vừa gõ filter — hãy đọc câu “NÓI”, rồi mới bấm.

### 0.6. Cách đọc một gói CollabNet (13 byte header) — hiểu một lần, dùng cả buổi

Mỗi datagram UDP của CollabNet có cấu trúc cố định:

```
+----------+----------------+---------------------+-------------------------------+----------+
| loại 1B  |  CID 4B        |  packet number 8B   |  phần thân (đã mã hoá)        | tag 16B  |
| 0x01     |  connection id |  tăng dần           |  frame STREAM/ACK/PING/...    | AES-GCM  |
| 0x02     |                |                     |                               |          |
| 0x10     |                |                     |                               |          |
+----------+----------------+---------------------+-------------------------------+----------+
            \____________ header 13 byte, được xác thực như AAD ____________/
```

| Giá trị byte đầu | Tên gói | Khi nào thấy | Kích thước UDP điển hình |
|---|---|---|---|
| `0x01` | INITIAL | Client chào server / chào peer P2P | `udp.length == 57` |
| `0x02` | HANDSHAKE | Server (hoặc peer) trả lời, có chữ ký | `udp.length == 153` |
| `0x10` | DATA | Mọi dữ liệu sau bắt tay, **đã mã hoá** | thay đổi, thường 60–1300 |

**Lưu ý:** `INITIAL` và `HANDSHAKE` là **bản rõ** (chỉ chứa khoá công khai và chữ ký), **không có tag**;
chỉ gói `DATA` mới được mã hoá và có 16 byte tag ở cuối. Đừng nói “mọi gói đều có tag” — sẽ bị bắt lỗi.

**Ba câu phải thuộc:**
1. “Byte đầu tiên cho biết loại gói: 01 là chào, 02 là chào đáp, 10 là dữ liệu đã mã hoá.”
2. “Với gói DATA, 13 byte đầu là header; 16 byte cuối là tag xác thực AES-GCM; ở giữa là phần thân mã hoá.”
3. “Trong Wireshark dùng `udp.payload[0]`, **không dùng** `udp[8]` — `udp.payload` là buffer riêng của UDP.”

### 0.7. Sáu thao tác Wireshark dùng đi dùng lại

**A. Chọn card loopback và bắt đầu bắt gói**
1. Mở Wireshark.
2. Nháy đúp vào **Adapter for loopback traffic capture** (hoặc chọn nó rồi bấm nút vây cá mập xanh).
3. Nếu muốn đặt capture filter trước khi bắt: gõ vào ô “Capture filter”:
   ```
   udp or tcp portrange 8080-8099
   ```
   rồi bấm Start. Capture filter này bắt **mọi UDP** (để không sót file P2P) và mọi TCP UI.

**B. Dừng / bắt lại**
- Dừng: bấm nút vuông đỏ (Ctrl+E).
- Bắt lại từ đầu: Ctrl+Shift+E (restart), hoặc Ctrl+E rồi Ctrl+E.

**C. Gõ display filter**
1. Bấm vào thanh filter xanh ở trên cùng (hoặc Ctrl+/).
2. Gõ biểu thức.
3. Bấm Enter hoặc mũi tên xanh “Apply”.
4. Thanh filter **xanh** = hợp lệ; **đỏ** = sai cú pháp, sửa theo đúng tài liệu này.
5. Xoá filter: bấm dấu X trong thanh filter.

**D. Thêm 3 cột cho dễ đọc**
1. Chuột phải lên tiêu đề cột bất kỳ → **Column Preferences…**
2. Bấm dấu **+** ba lần, điền:

| Title | Type | Fields |
|---|---|---|
| Kind | Custom | `udp.payload[0]` |
| CID | Custom | `udp.payload[1:4]` |
| PN | Custom | `udp.payload[5:8]` |

3. Bấm OK. Cột `Kind` hiện `01`, `02`, `10` (thập lục phân). Cột `PN` hiện 8 byte dạng
   `00:00:00:00:00:00:00:0a`; **hai nhóm hex cuối** là số thứ tự gói (ở đây là 0x0a = 10).

**E. Xem byte thô của một gói**
1. Bấm vào gói trong danh sách.
2. Ở khung giữa (Packet Details), mở dòng **User Datagram Protocol** → **Data**.
3. Ở khung dưới (Packet Bytes), các byte được tô sáng tương ứng.
4. Đọc byte đầu tiên ở góc trái: `01`, `02` hay `10`.

**F. Follow stream / thống kê**
- Chuột phải một gói → **Follow → UDP Stream** (hoặc **TCP Stream** với giao diện web).
- Menu **Statistics → Conversations** → chọn tab **UDP** hoặc **TCP**: thấy từng cặp cổng,
  số gói, số byte, thời lượng. Đây là bằng chứng mạnh nhất cho “có bao nhiêu client” và
  “file có đi qua server không”.

### 0.8. Lịch trình 18 phút

| Phút | Nội dung | Bước |
|---|---|---|
| 0:00–1:30 | Giới thiệu, kiến trúc, mở Wireshark | 0 + Bước 1 |
| 1:30–3:00 | Bắt tay, đăng nhập | Bước 2 |
| 3:00–4:30 | Xác thực, presence, 3 user | Bước 3 |
| 4:30–6:00 | Đồng thời, 3 client cùng lúc | Bước 4 |
| 6:00–8:30 | Chat chung/riêng + **offline nhận tin** | Bước 5 |
| 8:30–11:30 | **Gửi file vào chat chung** + file offline | Bước 6 |
| 11:30–13:30 | Mất kết nối, tự kết nối lại, mất gói | Bước 7 |
| 13:30–15:30 | Mã hoá, so sánh với HTTP nội bộ | Bước 8 |
| 15:30–17:00 | UI HTTP + SSE | Bước 9 |
| 17:00–18:30 | Kiểm thử, benchmark, tổng kết | Bước 10 |

Nếu bị cắt thời gian: bỏ phần “Nếu giảng viên hỏi”, giữ nguyên 4 phần chính của mỗi bước.

### 0.9. Câu mở đầu (đọc nguyên văn)

> “Em xin chào thầy/cô. Đồ án của em là **CollabNet** — ứng dụng cộng tác client-server chạy trên
> **UDP thuần** với giao thức tầng ứng dụng tự viết. Ứng dụng có chat chung, chat riêng, danh sách
> người đang online, gửi file có kiểm tra SHA-256, và vẫn nhận được tin nhắn cùng file sau khi
> người nhận đã đăng xuất. Giao diện là web HTML + JavaScript, nhưng toàn bộ dữ liệu cộng tác đi
> trên UDP tự viết, không dùng TCP, không dùng WebSocket, không dùng framework mạng.
> Em xin phép trình bày theo đúng 10 bước trong đề bài, mỗi bước em sẽ chỉ ra code, demo trên web
> và dùng Wireshark chứng minh gói tin tương ứng.”

---

## BƯỚC 1 — Setup & Protocol Design (1 điểm)

> **Mục tiêu chấm điểm:** “Define the custom packet structure, message types (e.g., AUTH, MSG, FILE),
> and state diagrams in documentation before coding.”

### 1.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 1 là thiết kế giao thức trước khi viết code. Em thiết kế một transport nhỏ kiểu QUIC chạy
> trên một socket UDP duy nhất. Mỗi datagram có **header 13 byte**: 1 byte loại gói, 4 byte
> connection id, 8 byte số thứ tự gói. Có ba loại gói: `INITIAL` mã `0x01`, `HANDSHAKE` mã `0x02`,
> và `DATA` mã `0x10`. Phần thân của gói `DATA` được mã hoá AES-256-GCM, 16 byte cuối là tag xác
> thực. Bên trong phần thân là các **frame** kiểu QUIC: `STREAM`, `ACK`, `MAX_STREAM_DATA`,
> `PING`, `CLOSE`. Mỗi tin nhắn hoặc mỗi file là một **stream riêng**, nên một gói chậm không chặn
> các luồng khác — đó là chống head-of-line blocking. Giao thức tầng ứng dụng nằm trong
> `common/protocol.py`: mỗi thông điệp là một JSON có tiền tố độ dài 4 byte, ví dụ `AUTH`, `MSG`,
> `PEERS`, `HISTORY`. State diagram và đặc tả gói nằm trong `docs/report.pdf` mục 2; code tương ứng
> là `common/packet.py` và `common/protocol.py`.”

**Nếu chỉ có 30 giây:** “Đây là header 13 byte và ba loại gói; phần thân mã hoá AES-GCM, bên trong
là các frame kiểu QUIC; mỗi tin nhắn là một stream riêng.”

### 1.2. Demo trên web

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Mở `docs/report.pdf`, trang kiến trúc | Sơ đồ 3 tầng: Browser → Gateway → ClientCore → UDP; Server ở giữa |
| 2 | Mở `common/packet.py` | Docstring vẽ đúng bố cục 13 byte + danh sách frame |
| 3 | Mở `common/protocol.py` | Docstring mô tả stream 0/1 và JSON có độ dài |
| 4 | Chuyển sang tab Alice, chỉ vào ô đăng nhập | Giao diện web; chưa bấm đăng nhập |

**Câu nói khi chỉ trang giấy:** “Em thiết kế trước khi code: header cố định 13 byte, frame nằm trong
phần mã hoá, mỗi tin nhắn một stream. Nhờ vậy phần còn lại của đồ án chỉ việc dùng lại giao thức này.”

### 1.3. Wireshark — chứng minh cấu trúc gói

**Chuẩn bị:** bắt đầu bắt gói trên card loopback **trước khi** đăng nhập (xem 0.7.A).

**Filter chính (dán vào thanh xanh):**

```
udp.port == 9000
```

**Cách tìm gói từng bước:**

1. Gõ filter trên, Enter. Bạn thấy hàng trăm gói UDP giữa các cổng ngẫu nhiên và cổng 9000.
2. Thêm 3 cột `Kind`, `CID`, `PN` như hướng dẫn 0.7.D.
3. Kéo thanh cuộn lên gói đầu tiên. Cột `Kind` phải là `01`.
4. Bấm gói `01` đầu tiên. Ở khung giữa mở **User Datagram Protocol → Data**.
5. Ở khung dưới, 13 byte đầu đang được tô sáng. Đọc to: “byte 0 là `01`, byte 1–4 là connection id,
   byte 5–12 là packet number; 36 byte còn lại là connection id của client và khoá công khai X25519.”

**Filter để chỉ thấy đúng một loại gói (dùng khi muốn chứng minh nhanh):**

```
udp.port == 9000 && udp.payload[0] == 0x01 && udp.length == 57
```

→ chỉ còn gói `INITIAL` (8 byte UDP header + 13 byte header + 36 byte thân = 57).

```
udp.port == 9000 && udp.payload[0] == 0x02 && udp.length == 153
```

→ chỉ còn gói `HANDSHAKE` (8 + 13 + 132 = 153).

```
udp.port == 9000 && udp.payload[0] == 0x10
```

→ chỉ còn gói `DATA` đã mã hoá.

**Bạn sẽ thấy gì:** danh sách gói có cột `Kind` xen kẽ `01`, `02`, `10`; các gói `10` chiếm đa số.
Khi bấm một gói `10`, phần thân sau 13 byte là các byte ngẫu nhiên, không đọc được chữ.

**Ý nghĩa gói tin:**

| Trường | Giá trị | Ý nghĩa |
|---|---|---|
| Byte 0 | `0x01` | INITIAL — client xin bắt tay |
| Byte 0 | `0x02` | HANDSHAKE — bên nhận trả lời, kèm chữ ký |
| Byte 0 | `0x10` | DATA — dữ liệu ứng dụng đã mã hoá |
| Byte 1–4 | CID | Connection ID: định tuyến datagram về đúng kết nối |
| Byte 5–12 | PN | Packet Number: tăng dần, làm nonce cho AES-GCM |
| Byte 13… | Ciphertext | Các frame STREAM/ACK/PING/CLOSE đã mã hoá |
| 16 byte cuối | GCM tag | Xác thực toàn vẹn; sửa 1 bit là gói bị loại |

**Câu nói khi đang chỉ màn hình:**

> “Thầy/cô thấy cột Kind: gói đầu tiên là `01` — client chào. Gói tiếp theo `02` — server trả lời.
> Từ đây trở đi toàn `10` — dữ liệu đã mã hoá. Header 13 byte luôn nhìn thấy được để định tuyến,
> nhưng phần thân thì Wireshark không đọc được, đó là chủ ý của bước 8.”

**Nếu không thấy gói:** xem Phụ lục E (sai card, chưa có Npcap loopback, hoặc đang lọc TCP thay vì UDP).

### 1.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Vì sao header không mã hoá? | Cần định tuyến datagram vào đúng connection và làm nonce; header được xác thực như AAD nên không sửa được. |
| Vì sao 13 byte? | 1 + 4 + 8 là đủ cho loại gói, connection id và số thứ tự gói; nhỏ để giảm overhead. |
| Sao không dùng TCP? | Đề yêu cầu UDP streaming và tự xây độ tin cậy ở tầng ứng dụng; TCP sẽ không cho kiểm soát stream/ACK/congestion. |
| Mỗi tin nhắn một stream để làm gì? | Chống head-of-line blocking: file lớn bị mất gói không chặn tin nhắn chat. |

---

## BƯỚC 2 — Basic Client-Server Handshake (1 điểm)

> **Mục tiêu chấm điểm:** “Implement basic TCP socket connection where a client can connect to the
> server and receive an acknowledgment.” — Đồ án dùng **UDP tự viết** thay cho TCP, nhưng vẫn có
> bắt tay và ACK đầy đủ; khi trình bày nói rõ điều này.

### 2.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 2 là bắt tay. Client sinh một cặp khoá **X25519 tạm thời**, gửi gói `INITIAL` gồm connection
> id và khoá công khai 32 byte. Server sinh khoá tạm của mình, rồi ký một **transcript** gồm khoá
> client, khoá server và hai connection id bằng khoá **Ed25519** của server. Server trả gói
> `HANDSHAKE` chứa connection id server, khoá công khai tạm, khoá công khai dài hạn và chữ ký 64 byte.
> Client kiểm tra chữ ký, kiểm tra fingerprint server đã ghim từ lần đầu (TOFU), rồi cả hai dùng
> **HKDF-SHA256** để dẫn ra hai khoá AES-256 riêng cho hai chiều. Từ gói tiếp theo, mọi thứ là `DATA`
> đã mã hoá. Nếu gói `INITIAL` bị mất, client gửi lại sau 0,25 giây, rồi 0,5 giây, rồi 1 giây.
> Sau bắt tay, client gửi `AUTH` trên stream điều khiển số 0; server trả `AUTH_OK` kèm danh sách
> peer. Đó là ‘acknowledgment’ của đồ án.”

**Nếu chỉ có 30 giây:** “INITIAL → HANDSHAKE → kiểm tra chữ ký → HKDF ra hai khoá AES → AUTH →
AUTH_OK; các gói sau đều là DATA mã hoá.”

### 2.2. Demo trên web

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Nếu Wireshark chưa bắt, bấm Start (hoặc Ctrl+Shift+E để bắt lại) | Cột gói bắt đầu chạy |
| 2 | Ở tab Alice nhập `alice` / `1234`, bấm **Đăng nhập** | Vào giao diện; góc trái dưới hiện “Đã kết nối” |
| 3 | Chỉ vào toast góc phải | “Đã ghi nhớ khoá của server (`ab12:…`)” — TOFU |
| 4 | Mở file `source\client_state_8080\known_hosts.json` | Cùng fingerprint với toast và với dòng server in ra |

Server ở cửa sổ console in ra:
```
CollabNet server on UDP port 9000 | congestion control: cubic
Server key fingerprint (clients pin this on first use): xx:xx:...
```
**Câu nói:** “Fingerprint này được client ghim lần đầu; nếu lần sau server đổi khoá, client từ chối
kết nối — đó là chống man-in-the-middle.”

### 2.3. Wireshark — bắt tay và ACK

**Filter chính:**

```
udp.port == 9000 && (udp.payload[0] == 0x01 || udp.payload[0] == 0x02)
```

**Cách tìm gói từng bước:**

1. Gõ filter, Enter. Bạn sẽ thấy cặp gói `01` rồi `02` ngay đầu capture.
2. Nếu thấy nhiều gói `01` giống nhau trước khi có `02`: đó là **gửi lại INITIAL** do chưa nhận
   trả lời; giải thích ngay “đây là retransmission của bắt tay, không phải lỗi”.
3. Bấm gói `01`. Ở khung giữa mở **Data**; gói dài đúng **57 byte UDP**. Đọc: 13 byte header,
   4 byte connection id client, 32 byte khoá X25519.
4. Bấm gói `02` ngay sau. Gói dài đúng **153 byte UDP**: 13 header + 4 scid + 32 khoá server +
   32 khoá Ed25519 dài hạn + 64 chữ ký.
5. Gói `10` ngay sau đó là `AUTH` đã mã hoá. Nếu muốn chứng minh, filter:
   ```
   udp.port == 9000 && udp.payload[0] == 0x10 && udp.length < 200
   ```
   → các gói nhỏ ngay sau bắt tay là AUTH/ACK; không đọc được nội dung.

**Filter chỉ thấy bắt tay server (bỏ bắt tay P2P):**

```
(udp.payload[0] == 0x01 || udp.payload[0] == 0x02) && udp.port == 9000
```

**Filter bắt tay P2P (xuất hiện khi bắt đầu gửi file):**

```
(udp.payload[0] == 0x01 || udp.payload[0] == 0x02) && udp.port != 9000 && udp.port != 9998
```

**Bạn sẽ thấy gì:** một cặp `01`/`02` cho mỗi lần client kết nối server; khi gửi file P2P, một cặp
`01`/`02` nữa giữa hai cổng ngẫu nhiên của hai client.

**Ý nghĩa gói tin:**

| Gói | Độ dài UDP | Nội dung sau header 13 byte | Ý nghĩa |
|---|---|---|---|
| INITIAL | 57 | 4 byte CID client + 32 byte X25519 client | Client chào, đề nghị khoá tạm |
| HANDSHAKE | 153 | 4 byte CID server + 32 byte X25519 server + 32 byte Ed25519 server + 64 byte chữ ký | Server trả lời, chứng minh danh tính |
| DATA đầu tiên | thay đổi | AES-256-GCM | `AUTH` gửi mật khẩu đã mã hoá |

**Câu nói khi đang chỉ màn hình:**

> “Đây là gói `01` dài 57 byte — đúng 13 byte header, 4 byte connection id và 32 byte khoá X25519.
> Gói `02` dài 153 byte — thêm 32 byte khoá server, 32 byte khoá dài hạn và 64 byte chữ ký Ed25519.
> Wireshark chỉ nhìn thấy các khoá công khai; khoá riêng không bao giờ lên đường truyền.”

**Nếu không thấy `02`:** kiểm tra server đang chạy và client trỏ đúng `127.0.0.1:9000`; nếu thấy
nhiều `01` lặp lại, đó là retransmission bình thường.

### 2.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Vì sao cần cả X25519 và Ed25519? | X25519 để thoả thuận khoá tạm (forward secrecy); Ed25519 để server chứng minh danh tính. |
| Chữ ký ký cái gì? | Transcript gồm khoá client, khoá server, CID client, CID server — chống phát lại sang phiên khác. |
| TOFU là gì? | Tin lần đầu, ghim fingerprint; lần sau khác thì từ chối. |
| Vì sao INITIAL lặp lại? | Chưa nhận HANDSHAKE thì gửi lại với backoff 0,25 → 0,5 → 1 giây. |
| ACK nằm ở đâu? | Trong frame ACK của gói DATA; Wireshark không đọc được vì đã mã hoá. |

---
## BƯỚC 3 — Authentication & State Management (1 điểm)

> **Mục tiêu chấm điểm:** “Implement a login mechanism. The server must track connected users,
> their IP addresses, and active ports.”

### 3.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 3 là đăng nhập và quản lý trạng thái. Server lưu tài khoản trong `server_data/users.json`,
> mật khẩu không lưu dạng chữ mà lưu **PBKDF2-HMAC-SHA256** với 120.000 vòng và muối ngẫu nhiên
> 16 byte. Lần đăng nhập đầu tiên sẽ tự đăng ký; các lần sau kiểm tra bằng `hmac.compare_digest`
> để tránh tấn công đo thời gian. Mỗi kết nối đã xác thực được đại diện bởi một `Session` chứa:
> tên người dùng, địa chỉ IP, cổng UDP của client, cổng P2P và fingerprint P2P. Server giữ từ điển
> `by_user` từ tên sang session. Khi có người vào hoặc ra, server phát `PEERS` cho mọi người, nên
> danh sách online ở giao diện luôn cập nhật. Mỗi tên chỉ có một session: đăng nhập ở nơi khác sẽ
> đá session cũ. Server còn lưu mốc tạo tài khoản trong `first_seen.json` để tài khoản mới không
> thấy tin chung phát sinh trước khi nó tồn tại. Toàn bộ trạng thái này nằm trong
> `server/server.py` lớp `Session`, `Server` và `server/users.py`.”

**Nếu chỉ có 30 giây:** “Đăng nhập bằng PBKDF2; server giữ `by_user` gồm tên, IP, cổng UDP, cổng P2P;
mỗi lần có người vào/ra thì phát `PEERS`; mỗi tên một session.”

### 3.2. Demo trên web

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Đăng nhập lần lượt `alice`, `bob`, `carol` ở 3 tab | Cả ba vào giao diện, trạng thái “Đã kết nối” |
| 2 | Ở tab Alice, nhìn cột trái | “Cả nhóm”, “Tin nhắn riêng” có `bob`, `carol`; tiêu đề chat chung ghi “3 người đang online” |
| 3 | Nhìn cửa sổ server | Log `user alice logged in from 127.0.0.1:xxxxx` kèm `(registered)` lần đầu hoặc `(welcome back)` lần sau |
| 4 | Mở `source\server_data\users.json` bằng Notepad | Chỉ thấy chuỗi `pbkdf2$120000$...`, **không** thấy mật khẩu `1234` |
| 5 | Mở `source\server_data\first_seen.json` | Mốc thời gian tạo tài khoản của từng người |
| 6 | Tab Bob bấm nút **Đăng xuất** (góc dưới bên trái) | Bob về màn hình đăng nhập; Alice và Carol thấy `bob` chuyển **Offline** (nếu đã có cuộc trò chuyện riêng) và số online giảm còn 2 |
| 7 | Tab Bob đăng nhập lại `bob` / `1234` | Bob vào lại; Alice và Carol thấy `bob` online trở lại |

**Câu nói khi chỉ vào `users.json`:** “Thầy/cô thấy file không có mật khẩu, chỉ có chuỗi băm PBKDF2
kèm muối và số vòng. Nếu file bị lộ, kẻ tấn công vẫn phải bẻ từng mật khẩu.”

### 3.3. Wireshark — đăng nhập, presence, beacon

#### 3.3.1. Bản rõ của thao tác đăng nhập (chỉ trên loopback)

**Filter:**

```
http.request.method == "POST" && http.request.uri == "/api/login"
```

**Cách tìm gói:**

1. Gõ filter, Enter. Bạn thấy đúng một gói POST `/api/login` cho mỗi lần đăng nhập.
2. Bấm gói đó. Ở khung giữa mở **JavaScript Object Notation: application/json**.
3. Mở tiếp các trường; thấy `user: "alice"`, `pass: "1234"`, `server: "127.0.0.1:9000"`.

**Ý nghĩa:** đây là đoạn **trình duyệt → gateway cục bộ** trên `127.0.0.1`, không phải dữ liệu đi
qua mạng LAN. Nó bản rõ vì cùng một máy; gateway chỉ bind `127.0.0.1`, kiểm tra header `Host` và
bắt buộc header `X-Requested-With`. Trên đường UDP thật, `AUTH` nằm trong gói `0x10` đã mã hoá.

**Câu nói:** “Đây là chỗ duy nhất thấy mật khẩu, và nó chỉ nằm trong máy. Ra khỏi máy, mật khẩu
nằm trong AUTH đã mã hoá AES-GCM.”

#### 3.3.2. AUTH đã mã hoá trên UDP

**Filter:**

```
udp.port == 9000 && udp.payload[0] == 0x10 && udp.length < 200
```

**Cách tìm gói:**

1. Bấm một gói ngay sau cặp `01`/`02` của lần đăng nhập.
2. Ở khung giữa mở **Data**. Không có chuỗi `alice` hay `1234`; chỉ có byte ngẫu nhiên.
3. Thử tìm chữ trong toàn bộ gói UDP bằng filter:
   ```
   udp.port == 9000 && frame contains "alice"
   ```
   → **0 packet**. Đây là bằng chứng tên đăng nhập không lộ trên đường truyền.

**Ý nghĩa:** `AUTH` là thông điệp JSON nằm trong stream điều khiển 0, đã được mã hoá; server trả
`AUTH_OK`, `PEERS`, `HISTORY` trên stream điều khiển 1, cũng đã mã hoá.

#### 3.3.3. Beacon tìm server trong LAN (bản rõ có chủ ý)

**Filter:**

```
udp.port == 9998
```

**Cách tìm gói:**

1. Gõ filter, Enter. Cứ khoảng 2 giây có một gói broadcast.
2. Bấm gói, mở **User Datagram Protocol → Data**.
3. Đọc được JSON:
   ```json
   {"svc":"collabnet","port":9000,"name":"CollabNet"}
   ```

**Ý nghĩa:** server tự quảng bá để client trong LAN tìm thấy mà không cần biết IP. Gói này bản rõ
vì chỉ chứa tên dịch vụ và cổng, không chứa bí mật. Đây là chức năng “Tìm trong LAN” trên màn hình
đăng nhập.

#### 3.3.4. Presence khi có người ra/vào

**Filter:**

```
udp.port == 9000 && udp.payload[0] == 0x10
```

**Cách tìm gói:**

1. Ghi lại thời điểm Bob bấm Đăng xuất (hoặc xem đồng hồ trên màn hình).
2. Trong Wireshark, cuộn tới đúng thời điểm đó.
3. Bạn thấy một đợt gói nhỏ từ server (cổng nguồn 9000) gửi tới các client còn lại — đó là `PEERS`
   cập nhật danh sách. Nội dung đã mã hoá, nhưng **thời điểm và số người nhận** khớp với UI.
4. Bấm **Statistics → Conversations → UDP**: bảng vẫn liệt kê hội thoại cũ (đã kết thúc), nhưng nếu bấm vào dòng của Bob, cột Packets không tăng thêm sau thời điểm logout.

**Câu nói:** “Wireshark không đọc được danh sách peer vì đã mã hoá, nhưng thầy/cô thấy ngay sau khi
Bob đăng xuất, server gửi một đợt gói cho Alice và Carol; từ mốc đó không còn gói mới nào tới cổng
của Bob.”

**Bảng ý nghĩa:**

| Gói / kênh | Nhìn thấy gì | Ý nghĩa |
|---|---|---|
| HTTP `POST /api/login` | JSON có `user`, `pass` | Bản rõ trong máy, browser → gateway loopback |
| UDP `0x10`, cổng 9000 | Byte ngẫu nhiên | `AUTH`, `AUTH_OK`, `PEERS`, `HISTORY` đã mã hoá |
| UDP cổng 9998 | JSON `svc/port/name` | Beacon quảng bá server, bản rõ có chủ ý |
| UDP `0x10` sau logout | Đợt gói nhỏ server → client | Cập nhật `PEERS` khi presence thay đổi |

### 3.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Mật khẩu lưu thế nào? | PBKDF2-HMAC-SHA256, 120.000 vòng, muối 16 byte, so sánh hằng thời gian. |
| Server theo dõi những gì? | Tên, IP, cổng UDP của session, cổng P2P, fingerprint P2P, thời điểm vào. |
| Đăng nhập cùng tên ở máy khác? | Session cũ bị đóng với lý do “logged in from another place”; session mới thay thế. |
| Tài khoản mới có thấy tin cũ? | Không thấy tin **chung** trước thời điểm tạo tài khoản; tin riêng chỉ phát sinh sau khi tài khoản tồn tại. |
| Vì sao beacon bản rõ? | Chỉ quảng bá tên dịch vụ và cổng; không có bí mật; client cần đọc trước khi có khoá. |

---

## BƯỚC 4 — Concurrency Implementation (1 điểm)

> **Mục tiêu chấm điểm:** “Integrate multi-threading or Async I/O so the server can handle multiple
> clients connecting and disconnecting simultaneously.”

### 4.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 4 là xử lý đồng thời. Server và client đều chạy trên **một event loop asyncio**, không tạo
> thread cho từng client. Server mở **một socket UDP duy nhất** ở cổng 9000. Mỗi datagram đến được
> đọc một lần, rồi phân phối cho đúng `Connection` dựa vào **connection id** trong header 13 byte.
> Mỗi connection có nhiều stream độc lập; mỗi stream có cửa sổ nhận riêng. Nhờ vậy một client chậm,
> một file lớn hay một gói mất không chặn các client khác. Trên Windows, `Endpoint` dùng
> `add_reader` nếu event loop hỗ trợ, nếu không thì một task `sock_recvfrom`; cả hai đều không chặn.
> Việc truyền file được đẩy sang **P2P giữa các client**, nên server chỉ xử lý tin nhắn và presence —
> đó là lý do một server nhỏ vẫn phục vụ được 10–20 client. Code chính ở `common/transport.py`
> (`Endpoint`, `Connection`) và `server/server.py` (`Session`, `by_user`).”

**Nếu chỉ có 30 giây:** “Một socket UDP, một event loop, phân phối theo connection id; không thread
per client; file đi P2P nên server không bị nghẽn.”

### 4.2. Demo trên web

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Đảm bảo cả 3 tab Alice/Bob/Carol đang online | Tiêu đề “Cả nhóm” ghi “3 người đang online” |
| 2 | Đặt 3 tab cạnh nhau | Mỗi tab là một tiến trình client riêng, cổng UI riêng |
| 3 | Gõ một tin ở Alice, ngay lập tức gõ tin ở Bob, rồi Carol | Cả ba khung chat cập nhật gần như cùng lúc, không tab nào bị treo |
| 4 | Mở panel phải (nút cạnh tên cuộc trò chuyện) ở cả 3 tab | Biểu đồ “Độ trễ”, “Cửa sổ gửi”, “Gói bị mất” chạy độc lập |
| 5 | Nhìn cửa sổ server | Các dòng log đăng nhập/đóng kết nối xen kẽ, không có dấu hiệu chờ tuần tự |

**Câu nói:** “Ba client này là ba tiến trình riêng, nhưng server chỉ có một socket UDP và một event
loop. Nếu là thread-per-client, em sẽ phải quản lý 3 thread; ở đây mọi thứ là bất đồng bộ.”

### 4.3. Wireshark — chứng minh nhiều client cùng lúc

**Filter chính:**

```
udp.port == 9000
```

**Cách tìm gói từng bước:**

1. Gõ filter, Enter.
2. Mở **Statistics → Conversations**, chọn tab **UDP**.
3. Bạn thấy **ba dòng** cùng trỏ tới cổng 9000, mỗi dòng là một cổng nguồn khác nhau của client
   (ví dụ `50001 ↔ 9000`, `50002 ↔ 9000`, `50003 ↔ 9000`), kèm số gói và số byte của từng client.
4. Đóng bảng. Mở **Statistics → Endpoints**, tab **UDP**: thấy `127.0.0.1:9000` và ba cổng client.
5. Chọn một dòng trong Conversations, bấm **Copy → As CSV** nếu muốn dán vào báo cáo.
6. Để chứng minh một client cụ thể: chọn một gói từ client đó, ghi lại **Source port**, rồi lọc:
   ```
   udp.port == 9000 && udp.srcport == 50001
   ```
   (thay `50001` bằng cổng thật).
7. Bấm **Statistics → I/O Graph**, thêm dòng filter `udp.port == 9000`, chọn “Packets per second”:
   thấy các đỉnh xen kẽ khi ba người cùng gửi.

**Bạn sẽ thấy gì:** ba cặp hội thoại UDP song song, không có cặp nào “chờ” cặp nào. Các gói từ ba
cổng nguồn khác nhau nằm xen kẽ trong cùng một khoảng mili-giây.

**Ý nghĩa:** mỗi dòng Conversations là một session đã xác thực. Cùng một IP `127.0.0.1` nhưng khác
cổng nguồn, nên Wireshark tách được 3 client. Nếu demo hai máy, cột địa chỉ sẽ khác IP thật.

**Câu nói khi chỉ bảng Conversations:**

> “Đây là bằng chứng định lượng: ba hội thoại UDP cùng tới cổng 9000, ba cổng nguồn khác nhau,
> số gói và số byte riêng. Server đang phục vụ cả ba trên cùng một socket.”

**Nếu chỉ thấy một dòng:** kiểm tra đã mở đủ 3 client và cả 3 đã đăng nhập chưa. Mỗi `Endpoint`
bind cổng 0 nên mỗi tiến trình phải có một cổng nguồn riêng. Nếu bảng đang bị lọc theo thời gian
hoặc theo địa chỉ, xoá bộ lọc và mở lại **Statistics → Conversations → UDP**; bỏ tick “Limit to
display filter” nếu đang bật.

### 4.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Vì sao không dùng thread? | Async I/O đủ cho I/O-bound; ít thread hơn, không cần khoá, dễ suy luận. |
| Một client chậm có chặn người khác? | Không: mỗi stream có cửa sổ riêng, dữ liệu lớn bị back-pressure tại stream đó. |
| Server chịu được bao nhiêu client? | Đề yêu cầu 10–20; kiến trúc một socket + event loop + file P2P đáp ứng thoải mái trong LAN. |
| File lớn có làm server chậm? | Không, byte file không đi qua server; chỉ có thẻ FILE_LOG nhỏ. |
| Nếu một client mất mạng? | Session bị đóng sau idle timeout; các session khác không ảnh hưởng. |

---

## BƯỚC 5 — Time-sensitive Streaming & Message Routing (1 điểm)

> **Mục tiêu chấm điểm:** “Implement the routing logic for clients to send messages to the server,
> and the server to broadcast or forward them to the correct recipient.”
>
> **Đây cũng là phần chứng minh yêu cầu số 1 của buổi demo:** User1 đăng xuất vẫn nhận được tin
> nhắn chung và riêng khi đăng nhập lại.

### 5.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 5 là định tuyến tin nhắn. Mỗi lần người dùng bấm gửi, client mở **một stream mới** — stream
> số chẵn — gửi một thông điệp `MSG` gồm id, người nhận và nội dung, rồi đóng stream bằng FIN.
> Server đọc header, thấy `to = "*"` thì phát cho **mọi session trừ người gửi**; thấy `to = "bob"`
> thì chỉ gửi cho session của Bob. Nếu Bob đang offline nhưng tài khoản tồn tại, server **vẫn lưu**
> tin vào `history.json` và gửi lại ngay sau khi Bob đăng nhập, trong thông điệp `HISTORY`. Server
> gán thời gian `ts` cho mỗi tin, nên mọi người sắp xếp hội thoại theo cùng một đồng hồ. Server trả
> `SENT` kèm số người nhận thực tế `n`; nếu người nhận chưa từng tồn tại thì trả `ERR`. Vì mỗi tin
> là một stream riêng, tin nhắn không phải chờ file lớn — đó là streaming nhạy thời gian, không bị
> head-of-line blocking. Code ở `ClientCore.send_message`, `Server._route_msg` và
> `HistoryStore.for_user`.”

**Nếu chỉ có 30 giây:** “Mỗi tin một stream; `*` là broadcast, tên là unicast; người offline vẫn
được lưu vào history và trả lại khi đăng nhập; server gán `ts` chung.”

### 5.2. Demo trên web — chat chung, chat riêng, offline

> **Chuẩn bị quan trọng:** trước khi Bob đăng xuất, Alice phải có cuộc trò chuyện riêng với Bob
> (xem 0.4). Nếu chưa, dòng `bob` sẽ biến mất khi Bob offline và Alice không bấm vào để gửi tiếp được.

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Tab Alice, chọn **Cả nhóm**, gửi “Chào cả nhóm” | Bob và Carol đều thấy tin; Alice thấy “Đã gửi tới 2 người đang online” |
| 2 | Tab Bob, chọn `alice`, gửi “Tin riêng của Bob” | Chỉ Alice thấy; tab Carol **không** thấy tin này |
| 3 | Tab Alice, chọn `bob`, gửi “Mình giữ cửa sổ chat này nhé” | Bob thấy; cuộc trò chuyện riêng tồn tại ở cả hai bên |
| 4 | Tab Bob bấm **Đăng xuất** | Bob về màn hình đăng nhập; cột trái của Alice hiện `bob` với nhãn **Offline** |
| 5 | Tab Alice bấm `bob` | Banner: “bob đang offline. Tin nhắn và file vẫn được gửi; họ sẽ thấy khi đăng nhập lại.” |
| 6 | Tab Alice gửi “Tin nhắn gửi lúc Bob offline” | Tin hiện ngay trong khung với trạng thái “Đã gửi”; banner phía trên đã báo Bob offline và sẽ thấy khi đăng nhập lại |
| 7 | Tab Alice chuyển sang **Cả nhóm**, gửi “Tin chung gửi lúc Bob offline” | Carol thấy ngay; Alice thấy “Đã gửi tới 1 người đang online” |
| 8 | Tab Bob đăng nhập lại `bob` / `1234` | Bob thấy **cả hai** tin: tin riêng trong cuộc `alice`, tin chung trong `Cả nhóm` |
| 9 | Tab Carol kiểm tra lại | Carol chỉ thấy tin chung, **không** thấy tin riêng Alice → Bob |
| 10 | Mở `source\server_data\history.json` | Có bản ghi `to: "*"` và `to: "bob"` với nội dung tương ứng |

**Câu nói khi Bob đăng nhập lại:** “Đây là yêu cầu số 1: Bob đã đăng xuất, Alice vẫn gửi được tin
riêng và tin chung; khi Bob vào lại, server trả `HISTORY` và Bob thấy đúng cả hai, đúng cuộc trò
chuyện, đúng thứ tự thời gian.”

**Giải thích nếu giảng viên hỏi vì sao Bob thấy tin cũ:** server là nguồn lưu lịch sử duy nhất;
client không giữ lịch sử giữa các phiên. Sau khi xác thực, server gửi `HISTORY`; client dựng lại
hội thoại. Đăng xuất rồi tắt máy vẫn còn.

### 5.3. Wireshark — định tuyến và bằng chứng offline

#### 5.3.1. Mỗi tin nhắn là một request UI riêng

**Filter:**

```
http.request.method == "POST" && http.request.uri == "/api/send"
```

**Cách tìm gói:**

1. Gõ filter, Enter.
2. Mỗi lần bấm gửi, danh sách tăng đúng một dòng.
3. Bấm một dòng, mở **JavaScript Object Notation: application/json**; thấy:
   ```json
   {"to":"bob","text":"Tin nhắn gửi lúc Bob offline"}
   ```
4. Với tin chung, trường `to` là `"*"`.

**Ý nghĩa:** request này chỉ đi từ trình duyệt tới gateway trên cùng máy. Gateway mới là bên mở
stream UDP tới server. Nhìn request này để biết **ý định**; nhìn UDP để biết **gói thật**.

#### 5.3.2. Chiều client → server và server → client

**Filter chiều lên:**

```
udp.dstport == 9000 && udp.payload[0] == 0x10
```

**Filter chiều xuống:**

```
udp.srcport == 9000 && udp.payload[0] == 0x10
```

**Cách tìm gói:**

1. Bấm gửi một tin chung khi cả 3 người online. Ở filter chiều lên, bạn thấy một cụm gói nhỏ từ
   client Alice tới 9000.
2. Ở filter chiều xuống, bạn thấy **hai** cụm gói nhỏ từ 9000 tới hai cổng client Bob và Carol
   (broadcast trừ người gửi).
3. Gửi một tin riêng Bob → Alice. Chiều xuống chỉ còn **một** cụm tới cổng Alice; Carol không có gói.
4. Để chắc chắn, lọc theo cổng của Carol (lấy từ Conversations) và chứng minh không có gói tin riêng.

**Bạn sẽ thấy gì:** số cụm gói chiều xuống đúng bằng số người nhận. Nội dung đã mã hoá nên không
đọc được chữ, nhưng **số người nhận** khớp với thông báo trên UI (`n = 2`, `n = 1`, `n = 0`).

**Ý nghĩa:** server không gửi file hay tin qua một kênh khác; tất cả là các frame `STREAM` trong
gói `DATA`, mỗi tin một stream, nên không bị chặn bởi tin trước.

#### 5.3.3. Bằng chứng mạnh nhất: Bob offline thì **không có gói nào** tới Bob

Đây là màn quan trọng nhất của yêu cầu số 1. Làm đúng thứ tự:

1. Khi Bob còn online, mở **Statistics → Conversations → UDP**, tìm dòng của Bob và ghi lại **cổng
   UDP của Bob** (cổng nguồn phía client, ví dụ `50002`). Ghi ra giấy.
2. Cho Bob đăng xuất. Bấm **Clear display filter** (dấu X) rồi nhập:
   ```
   udp.srcport == 9000 && udp.dstport == 50002
   ```
   → **0 packet** (Bob không còn session).
3. Alice gửi tin riêng “Tin nhắn gửi lúc Bob offline”. Giữ nguyên filter.
   → vẫn **0 packet**: server không gửi tới Bob vì Bob offline; tin được ghi vào `history.json`.
4. Bấm **Statistics → Conversations**: hội thoại cũ của Bob vẫn nằm trong danh sách lịch sử (Wireshark không xoá dòng đã bắt), nhưng không có gói mới nào tới cổng đó; số gói của dòng Bob đứng yên.
5. Bob đăng nhập lại. Bob có **cổng UDP mới** (vì client mở endpoint mới). Xoá filter, cuộn tới
   thời điểm Bob đăng nhập: bạn thấy một cụm gói từ 9000 tới cổng mới của Bob — đó là `HISTORY`
   chứa tin nhắn và thẻ file đã lưu.

**Câu nói khi filter trả về 0 packet:**

> “Thầy/cô thấy không có một gói nào từ server tới cổng cũ của Bob trong lúc Bob offline. Đó chính
> là bằng chứng server **không gửi trực tiếp** mà **lưu** tin. Khi Bob đăng nhập lại, một cổng mới
> xuất hiện và server đẩy HISTORY — trên web, Bob thấy đúng tin cũ.”

**Lưu ý:** cổng UDP của Bob thay đổi sau mỗi lần đăng nhập vì client tạo endpoint mới. Đừng dùng
cổng cũ để tìm gói sau khi Bob vào lại; hãy lấy cổng mới từ Conversations.

#### 5.3.4. Bảng ý nghĩa

| Giá trị / gói | Nhìn thấy gì | Ý nghĩa |
|---|---|---|
| `to: "*"` | Nhiều cụm gói server → client | Broadcast tới mọi session trừ người gửi |
| `to: "bob"` | Một cụm gói tới cổng Bob | Unicast đúng người nhận |
| Bob offline | 0 gói tới cổng Bob | Server lưu `history.json`, không gửi trực tiếp |
| Bob đăng nhập lại | Cụm gói tới cổng mới | `HISTORY` trả lại tin và thẻ file |
| `SENT {n}` | UI “Đã gửi tới n người” | Số người nhận thực tế lúc gửi |
| `ERR` | UI “Người nhận đang offline” | Chỉ khi tên chưa từng tồn tại; người có tài khoản đang offline vẫn nhận được, không báo lỗi |

### 5.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Vì sao tin nhắn không bị chặn bởi file lớn? | Mỗi tin/mỗi file một stream riêng; mất gói ở stream này không chặn stream khác. |
| Thứ tự tin nhắn do ai quyết định? | Server gán `ts`; client sắp xếp theo `ts` chung, nên đến muộn vẫn đúng thứ tự. |
| Tin nhắn có được lưu trên server không? | Có, `history.json`, tối đa 4000 bản ghi; mỗi lần đăng nhập trả tối đa 300 tin gần nhất. |
| Gửi cho người chưa từng tồn tại? | Server trả `ERR` và UI báo “Người nhận đang offline”. |
| Tài khoản mới có thấy tin chung cũ? | Không; `first_seen.json` chặn tin chung trước thời điểm tạo tài khoản. |
| Nếu người gửi thoát trước khi người nhận online? | Tin nhắn đã lưu trên server nên vẫn còn; file thì nằm trong outbox của người gửi và chỉ gửi khi người gửi online lại. |

---

## BƯỚC 6 — Reliable File Transfer (1 điểm)

> **Mục tiêu chấm điểm:** “Implement file serialization, chunking (for large files), and reassembly
> over UDP without data corruption.”
>
> **Đây cũng là phần chứng minh yêu cầu số 2:** mọi người gửi được file vào **chat chung**, và
> User1 nhận được file gửi trong lúc đã đăng xuất.

### 6.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 6 là truyền file tin cậy. Điểm khác biệt của đồ án: **byte của file không đi qua server**.
> Mỗi client mở một cổng UDP P2P riêng và công bố cổng cùng fingerprint Ed25519 của mình qua
> server. Khi Alice gửi file cho Bob, Alice kết nối trực tiếp tới cổng P2P của Bob, xác minh đúng
> fingerprint, rồi mở một stream mới. File được đọc từng khối 64 KB ở tầng ứng dụng; transport chia
> tiếp thành các datagram tối đa 1200 byte để không vượt MTU, mỗi datagram có số thứ tự và được
> ACK chọn lọc. Bên nhận ghi vào file `.part`, tính **SHA-256** song song, so với SHA-256 trong gói
> `FILE_END`; khớp mới đổi tên thành file thật, lệch thì xoá và báo lỗi. Chat chung là **fan-out**:
> gửi P2P tới từng người đang online. Người đang offline thì server chỉ lưu **thẻ file** (tên, kích
> thước, SHA-256), còn byte nằm trong **outbox** của người gửi và được đẩy P2P ngay khi người nhận
> đăng nhập lại. Code ở `ClientCore.send_file`, `_p2p_push`, `_flush_one`, `_file_finish`.”

**Nếu chỉ có 30 giây:** “File đi P2P, chia datagram 1200 byte, ACK chọn lọc, SHA-256 kiểm tra;
chat chung fan-out; người offline nhận sau nhờ thẻ file + outbox.”

### 6.2. Tạo file demo và demo gửi file

**Tạo file 5 MB ngẫu nhiên (làm trước khi demo):**

```bat
cd /d "C:\Users\hvy14\Documents\Mạng Máy Tính\Assignment\ASS1\source"
..\.venv\Scripts\python.exe -c "import os; open('demo_5mb.bin','wb').write(os.urandom(5*1024*1024))"
copy demo_5mb.bin offline_5mb.bin
copy demo_5mb.bin group_offline_5mb.bin
```

**Gửi file vào chat chung (yêu cầu số 2):**

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Tab Alice, chọn **Cả nhóm** | Tiêu đề “Cả nhóm”, ô nhập ghi “Nhắn hoặc gửi file cho cả nhóm” |
| 2 | Bấm nút **kẹp giấy** cạnh ô nhập | Hộp chọn file của Windows mở ra |
| 3 | Chọn `demo_5mb.bin`, bấm Open | Thẻ file hiện trong khung chung, có thanh tiến trình, phần trăm, tốc độ, thời gian còn lại |
| 4 | Nhìn tab Bob và Carol | Thẻ file xuất hiện, tiến trình chạy, kết thúc “Đã nhận 5 MB” |
| 5 | Tab Bob bấm nút tải xuống trên thẻ file | File được lưu vào `client_state_8081\downloads\demo_5mb.bin` |
| 6 | Mở Command Prompt, chạy `certutil -hashfile demo_5mb.bin SHA256` ở thư mục gốc và trong `downloads` | Hai chuỗi SHA-256 **giống hệt nhau** |
| 7 | Tab Alice mở panel phải | Mục “Tất cả tệp đã chia sẻ” có `demo_5mb.bin` |

**Gửi file riêng:**

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Tab Bob chọn `alice`, bấm kẹp giấy, chọn một file nhỏ | Alice nhận; Carol không thấy thẻ file |
| 2 | Tab Alice bấm tải xuống, kiểm tra hash | Khớp với file gốc |

**Gửi file cho Bob đang offline (yêu cầu số 1, phần file):**

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Cho Bob đăng xuất (như bước 5) | Alice vẫn thấy dòng `bob` Offline |
| 2 | Tab Alice chọn `bob`, bấm kẹp giấy, chọn `offline_5mb.bin` | Thẻ file trạng thái “Sẽ gửi khi người nhận online” |
| 3 | Mở `source\client_state_8080\outbox\index.json` | Có mục cho file, `"to":"bob"`, `"delivered":[]` |
| 4 | Tab Bob đăng nhập lại | Thẻ file xuất hiện trong cuộc `alice`, trạng thái “Đang chờ người gửi truyền file”, rồi tự chuyển “Đang nhận…” và “Đã nhận 5 MB” |
| 5 | Kiểm tra hash file Bob nhận | Khớp SHA-256 với file gốc |
| 6 | Mở lại `outbox\index.json` | Mục file riêng đã biến mất sau khi gửi xong (file nhóm vẫn được giữ có chủ ý) |

**Câu nói khi Bob nhận file offline:** “Alice gửi lúc Bob đăng xuất. Server chỉ lưu thẻ file; byte
nằm trong outbox của Alice. Khi Bob vào lại, server phát PEERS, Alice thấy Bob online và đẩy file
P2P. Bob nhận đủ, SHA-256 khớp.”

**Gửi file vào chat chung khi Bob offline (yêu cầu 1 + 2):**

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Bob đang offline; tab Alice chọn **Cả nhóm** | Tiêu đề “Cả nhóm”; Carol vẫn online |
| 2 | Alice bấm kẹp giấy, chọn `group_offline_5mb.bin` | Carol nhận file ngay; thẻ file xuất hiện trong chat chung |
| 3 | Mở `source\client_state_8080\outbox\index.json` | Mục file nhóm có `"to":"*"`, `"delivered":["carol"]` (thường là vậy) |
| 4 | Bob đăng nhập lại | Thẻ file nhóm xuất hiện trong `Cả nhóm`; Bob tự động nhận file |
| 5 | Kiểm tra SHA-256 ở Bob | Khớp với file gốc |
| 6 | Mở lại `outbox\index.json` | Mục `"to":"*"` **vẫn còn** — file nhóm được giữ để người vào sau còn nhận được |

**Câu nói:** “Đây là yêu cầu số 1 áp dụng cho chat chung: Bob vắng mặt, Alice vẫn gửi file vào nhóm;
Carol nhận ngay, Bob nhận khi đăng nhập lại. File nhóm được giữ trong outbox có chủ ý, khác file
riêng đã giao xong thì xoá.”

**Wireshark cho màn này:** lúc Alice gửi, filter P2P chỉ thấy **một** luồng lớn tới Carol; khi Bob
đăng nhập, xuất hiện thêm **một** luồng lớn tới Bob. Đó là bằng chứng fan-out theo từng người nhận.

### 6.3. Wireshark — chứng minh file đi P2P, không qua server

#### 6.3.1. Tìm luồng file P2P

**Filter chính:**

```
udp.port != 9000 && udp.port != 9998 && udp.length > 1000
```

**Cách tìm gói từng bước:**

1. Bấm gửi file ở Alice. Ngay khi tiến trình chạy, gõ filter trên, Enter.
2. Bạn thấy hàng nghìn gói ~1200 byte giữa hai cổng ngẫu nhiên. Đây là các chunk của file.
3. Bấm một gói bất kỳ, ghi lại **Source port** và **Destination port**. Cả hai đều **khác** 9000 và 9998.
4. Lọc riêng luồng đó:
   ```
   udp.port == 54321
   ```
   (thay bằng một trong hai cổng vừa ghi).
5. Mở **Statistics → Conversations → UDP**: dòng có số byte lớn nhất chính là file; số byte xấp xỉ
   kích thước file cộng overhead. Với chat chung có 2 người nhận, bạn thấy **hai** dòng lớn.

**Bạn sẽ thấy gì:** các gói dữ liệu gần đầy MTU, xen kẽ các gói ACK nhỏ. Không có gói nào tới cổng
9000 chứa byte file.

#### 6.3.2. Chứng minh file **không** đi qua server

**Filter:**

```
udp.port == 9000 && udp.length > 1000
```

**Cách tìm gói:**

1. Trong lúc file đang chạy, gõ filter này, Enter.
2. Bạn thấy **rất ít hoặc 0 gói**, và không gói nào chứa hàng nghìn byte dữ liệu file.
3. So sánh với filter P2P ở trên: hàng nghìn gói lớn nằm ngoài cổng 9000.

**Câu nói:** “Nếu file đi qua server, thầy/cô sẽ thấy hàng nghìn gói lớn trên cổng 9000. Ở đây cổng
9000 chỉ có gói nhỏ điều khiển; toàn bộ byte file nằm ở cổng ngẫu nhiên — đó là P2P.”

#### 6.3.3. Bắt tay P2P trước khi truyền

**Filter:**

```
(udp.payload[0] == 0x01 || udp.payload[0] == 0x02) && udp.port != 9000 && udp.port != 9998
```

**Cách tìm gói:**

1. Ngay trước khi các gói lớn xuất hiện, có một cặp `01`/`02` giữa hai cổng P2P.
2. Gói `01` dài 57 byte, gói `02` dài 153 byte — giống bắt tay server nhưng giữa hai client.
3. Đây là lúc Alice xác minh fingerprint Ed25519 của Bob trước khi gửi byte.

#### 6.3.4. Phía giao diện web (bản rõ trong máy)

**Filter upload:**

```
http.request.method == "POST" && http.request.uri == "/api/upload"
```

**Cách tìm gói:**

1. Bấm một request upload. Ở khung giữa mở **Hypertext Transfer Protocol**.
2. Mở các header `X-To`, `X-Filename`, `X-File-Id`:
   - gửi nhóm: `X-To: *`
   - gửi riêng: `X-To: bob`
3. Thân request là byte file; dung lượng đúng bằng kích thước file. Đây là chặng browser → gateway
   trên cùng máy, chưa phải chặng P2P.

**Filter download:**

```
http.request.uri contains "/api/download/"
```

→ request tải file về trình duyệt; response có `Content-Disposition: attachment`.

#### 6.3.5. Bằng chứng file gửi cho Bob offline

1. Không cần ghi cổng P2P của Bob. Chỉ cần một mốc thời gian: bấm Clear display filter trước khi
   Bob đăng xuất.
2. Cho Bob đăng xuất. Alice gửi `offline_5mb.bin` cho Bob.
3. Filter:
   ```
   udp.port != 9000 && udp.port != 9998 && udp.length > 1000
   ```
   → **không có** luồng file mới, vì Bob không còn cổng P2P. Chỉ có request HTTP upload trong máy.
4. Mở `client_state_8080\outbox\index.json`: thấy file chờ, `delivered: []`.
5. Bob đăng nhập lại. Trong vòng vài giây, filter trên xuất hiện **một luồng lớn mới**; đó là
   Alice đẩy file P2P tới cổng mới của Bob.
6. Bob nhận xong, `outbox\index.json` mất mục file riêng.

**Câu nói:** “Trong lúc Bob offline, không có luồng P2P nào tới Bob. File nằm trong outbox của
Alice. Khi Bob vào lại, PEERS báo Bob online, Alice tự động đẩy file — đúng yêu cầu: gửi được lúc
người nhận vắng mặt và nhận lại khi đăng nhập.”

#### 6.3.6. Bảng ý nghĩa

| Gói / trường | Nhìn thấy gì | Ý nghĩa |
|---|---|---|
| P2P `0x01` / `0x02` | Cặp 57 / 153 byte ngoài cổng 9000 | Bắt tay client ↔ client, xác minh fingerprint |
| P2P `0x10`, `udp.length > 1000` | Hàng nghìn gói ~1200 byte | Chunk file; không qua server |
| P2P `udp.length < 80` | Gói nhỏ xen kẽ | ACK / keep-alive |
| HTTP `POST /api/upload` | Header `X-To: *` hoặc `X-To: bob` | Ý định gửi nhóm / riêng từ UI |
| HTTP `GET /api/download/...` | Response attachment | Tải file đã nhận |
| `outbox\index.json` | `to`, `delivered` | Hàng đợi byte cho người offline |

### 6.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Làm sao biết file không hỏng? | SHA-256 tính song song khi nhận; so với SHA-256 trong `FILE_END`; lệch thì xoá `.part`. |
| Chunk lớn bao nhiêu? | Ứng dụng đọc 64 KB; transport chia thành datagram tối đa 1200 byte để dưới MTU. |
| Gửi nhóm cho 3 người thì sao? | Fan-out P2P: một kết nối tới từng người đang online; ai offline nhận sau. |
| File lớn có tràn RAM? | Không: đọc/ghi theo chunk, có back-pressure `drain`; bên nhận ghi `.part` ngay. |
| Có resume khi đứt giữa chừng? | Không resume từng phần; bên nhận xoá `.part`, bên gửi gửi lại từ đầu. Đây là giới hạn đã biết. |
| Vì sao P2P? | Giảm tải server, tăng tốc trong LAN, và chứng minh transport tự viết chạy được client ↔ client. |
| Firewall chặn P2P? | UI báo “Không kết nối trực tiếp (P2P) được…”; cần mở UDP hoặc tắt firewall cho demo. |

---
## BƯỚC 7 — Network Resilience & Error Handling (1 điểm)

> **Mục tiêu chấm điểm:** “Implement try/except blocks to handle socket timeouts, broken pipes, and
> graceful client exits without crashing the server.”

### 7.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 7 là chịu lỗi. Transport tự phát hiện mất gói bằng ba cách: nếu có ba gói sau một gói chưa
> được ACK, hoặc quá 9/8 RTT, hoặc timer PTO hết hạn, gói đó bị coi là mất. Bên nhận gửi **ACK
> chọn lọc** dạng các khoảng packet number, nên bên gửi chỉ gửi lại đúng khoảng byte còn thiếu,
> không gửi lại cả file. Khi rảnh, hai bên gửi `PING` mỗi 4 giây; sau 20 giây không thấy gì thì
> **idle timeout** đóng kết nối. Phía client, nếu mất kết nối thì tự thử lại với backoff 1, 2, 4,
> 8, 15 giây; nếu server từ chối mật khẩu thì dừng hẳn và báo UI, không thử vô ích. Phía server,
> mọi dữ liệu sai giao thức bị bắt ở `ProtocolError`, chỉ đóng kết nối vi phạm, không làm sập
> server; lỗi bất ngờ được log lại. File đang nhận dở thì xoá `.part`; file gửi dở có nút **Gửi
> lại**; file chờ người offline nằm trong outbox. Đăng xuất gửi frame `CLOSE` và đóng êm. Code ở
> `common/transport.py` (PTO, loss detection, keep-alive) và `client/core.py` (`_reconnect`).”

**Nếu chỉ có 30 giây:** “PTO + ACK chọn lọc + keep-alive 4 giây + idle 20 giây; client tự kết nối
lại có backoff; server bắt lỗi giao thức và không sập; file dở thì xoá `.part` hoặc gửi lại.”

### 7.2. Demo trên web — mất server, tự kết nối lại, mất gói

#### 7.2.1. Tắt server rồi bật lại

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Cả 3 tab đang online, có vài tin nhắn | Trạng thái “Đã kết nối” |
| 2 | Cửa sổ server bấm Ctrl+C | Server dừng; sau tối đa ~20 giây (idle timeout), cả 3 tab hiện banner “Mất kết nối… Đang thử kết nối lại”. Trong lúc chờ, giải thích cơ chế idle timeout |
| 3 | Chờ tiếp | Banner vẫn còn; các tab tự thử lại, không treo |
| 4 | Bật lại server bằng đúng lệnh cũ | Trong tối đa 15 giây, cả 3 tab tự về “Đã kết nối”; không cần đăng nhập lại |
| 5 | Nhìn khung chat sau khi kết nối lại | Lịch sử cũ vẫn còn (server gửi lại `HISTORY` sau AUTH) |
| 6 | Gửi thử một tin mới | Tin đi bình thường |

**Câu nói:** “Em không bấm đăng nhập lại. Client tự phát hiện mất kết nối, thử lại với backoff, và
khi server trở lại thì tự bắt tay mới. Lịch sử vẫn còn vì server là nguồn lưu trữ.”

**Lưu ý:** trong lúc mất kết nối, ô nhập bị vô hiệu hoá; tin đang gõ không được tự động gửi sau.
Đây là hành vi có chủ ý để tránh gửi nhầm — nếu giảng viên hỏi, trả lời thẳng như vậy.

#### 7.2.2. Đóng client đột ngột

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Cửa sổ client Bob bấm Ctrl+C (không bấm Đăng xuất) | Tab Bob mất kết nối; Alice và Carol thấy Bob Offline sau tối đa ~20 giây (idle timeout) |
| 2 | Khởi động lại client Bob ở cổng 8081 | Mở tab 8081, đăng nhập `bob` / `1234` |
| 3 | Bob mở lại cuộc chat | Tin nhắn cũ vẫn còn; file đã nhận vẫn nằm trong `downloads` |

**Câu nói:** “Server không sập khi một client biến mất; nó chỉ gỡ session và phát PEERS. Bob vào lại
thì lịch sử được trả về từ server.”

#### 7.2.3. Mô phỏng mạng mất gói

Dừng server, rồi bật lại với tham số mô phỏng (chỉ cần mất gói ở chiều server → client là đủ thấy):

```bat
..\.venv\Scripts\python.exe -m server.server --port 9000 --sim-loss 0.05 --sim-delay-ms 20
```

Muốn mất gói cả hai chiều, khởi động lại một client với cùng tham số:

```bat
..\.venv\Scripts\python.exe -m client.main --ui-port 8080 --server 127.0.0.1:9000 --sim-loss 0.05 --sim-delay-ms 20
```

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Gửi 5–10 tin nhắn qua lại | Tin vẫn đến đủ, có thể chậm hơn một chút |
| 2 | Mở panel phải | “Gói bị mất” tăng, ví dụ `12 / 480 (2,5%)`; RTT tăng nhẹ |
| 3 | Gửi một file 5 MB | File vẫn nhận đủ, SHA-256 vẫn khớp |
| 4 | Quan sát thanh tiến trình | Có lúc chững lại rồi tiếp tục — đó là gửi lại |

**Câu nói:** “Em cố tình làm mất 5% gói. Giao diện vẫn nhận đủ tin và file, vì transport phát hiện
mất và gửi lại chọn lọc. Đây là bằng chứng độ tin cậy nằm ở tầng ứng dụng, không phải TCP.”

### 7.3. Wireshark — nhìn dấu vết mất gói và phục hồi

#### 7.3.1. Khoảng trống packet number

**Filter:**

```
udp.port == 9000 && udp.payload[0] == 0x10
```

**Cách tìm gói từng bước:**

1. Bật capture **trước** khi bật server với `--sim-loss 0.05`.
2. Nếu chỉ server có `--sim-loss`: gói bị bỏ ở chiều **server → client**. Lấy cổng UDP của một
   client từ **Statistics → Conversations**, rồi lọc:
   ```
   udp.port == 9000 && udp.srcport == 9000 && udp.dstport == 50001 && udp.payload[0] == 0x10
   ```
   (thay `50001` bằng cổng client).
3. Nếu client cũng chạy `--sim-loss`: gói bị bỏ ở chiều **client → server**. Lọc:
   ```
   udp.port == 9000 && udp.srcport == 50001 && udp.payload[0] == 0x10
   ```
4. Thêm cột `PN` (0.7.D). Đọc dãy số: `... 0x28, 0x29, 0x2c, 0x2d ...` — thiếu `0x2a`, `0x2b`.
5. Đó là các gói bị `--sim-loss` bỏ **trước khi** gửi ra card mạng, nên Wireshark không thấy.
6. Nhìn UI: tin nhắn vẫn đến đủ. Vì sau khoảng trống, các gói mới mang dữ liệu được gửi lại
   (retransmission lấy packet number mới, không dùng lại số cũ).

**Câu nói:** “Thầy/cô thấy số thứ tự gói nhảy từ 29 sang 2c — mất 2a và 2b. Nhưng trên web tin nhắn
vẫn hiện đủ. Nghĩa là transport đã phát hiện và gửi lại. Wireshark không tự gắn nhãn
‘retransmission’ cho UDP như với TCP, nên em chứng minh bằng khoảng trống số gói cộng với việc UI
vẫn nhận đủ.”

#### 7.3.2. Keep-alive khi rảnh

**Filter:**

```
udp.port == 9000 && udp.length < 70
```

**Cách tìm gói:**

1. Để yên 10–15 giây, không gửi gì.
2. Gõ filter, Enter. Bạn thấy các gói nhỏ cách nhau khoảng 4 giây theo mỗi chiều.
3. Đó là frame `PING` và `ACK` đã mã hoá; kích thước nhỏ vì không mang dữ liệu ứng dụng.

**Ý nghĩa:** keep-alive giúp phát hiện kết nối chết và giữ NAT mở. Nếu không có gói nào trong 20
giây, transport coi là idle timeout và đóng.

#### 7.3.3. Bắt tay lại sau khi server khởi động lại

**Filter:**

```
udp.port == 9000 && udp.payload[0] == 0x01
```

**Cách tìm gói:**

1. Giữ capture chạy trong lúc Ctrl+C server rồi bật lại.
2. Sau khi server lên, trong vòng tối đa khoảng 20–30 giây bạn thấy các gói `01` mới từ cả 3 client.
3. Theo sau là `02` rồi `10` — đúng một chu trình bắt tay mới.

**Câu nói:** “Đây là bằng chứng client tự kết nối lại: sau khi server sống lại, ba gói INITIAL mới
xuất hiện, tương ứng ba client tự bắt tay lại mà em không bấm gì.”

#### 7.3.4. Đăng xuất êm

**Filter:**

```
udp.port == 9000 && udp.payload[0] == 0x10
```

1. Trước khi Bob bấm Đăng xuất, ghi lại thời điểm.
2. Sau khi bấm, cuộn tới thời điểm đó: có một đợt gói nhỏ cuối cùng rồi im lặng.
3. Cửa sổ server in `connection 127.0.0.1:xxxxx (bob) closed: bye`.

**Ý nghĩa:** client gửi frame `CLOSE` (đã mã hoá) trước khi đóng socket; server log lý do `bye`.
Đây là thoát êm, khác với Ctrl+C (đóng đột ngột, server log `closed: ...` không có `bye`).

#### 7.3.5. Bảng ý nghĩa

| Hiện tượng | Nhìn thấy gì | Ý nghĩa |
|---|---|---|
| Mất gói mô phỏng | Khoảng trống PN | Gói bị bỏ trước khi ra card mạng |
| Gửi lại | Gói mới sau khoảng trống, UI vẫn đủ | PTO/loss detection + retransmission |
| Rảnh | Gói nhỏ mỗi ~4 giây | PING keep-alive |
| Server restart | Chuỗi `01` → `02` mới | Client tự reconnect + bắt tay mới |
| Đăng xuất | Đợt cuối rồi im lặng | Frame CLOSE, thoát êm |

### 7.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Làm sao phát hiện mất gói trên UDP? | Ba gói sau một gói chưa ACK, hoặc quá 9/8 RTT, hoặc PTO hết hạn. |
| SACK là gì? | ACK chứa các khoảng packet number đã nhận; bên gửi chỉ gửi lại khoảng thiếu. |
| Idle timeout bao lâu? | 20 giây; keep-alive 4 giây. |
| Client thử lại bao lâu? | Backoff 1 → 2 → 4 → 8 → 15 giây, lặp tới khi được hoặc bị từ chối mật khẩu. |
| Tin đang gõ lúc mất mạng có được gửi? | Không; UI vô hiệu hoá ô nhập để tránh gửi nhầm. |
| File đang nhận dở thì sao? | Bên nhận xoá `.part`; bên gửi báo lỗi và có nút Gửi lại. |
| Server có sập khi client gửi rác? | Không; `ProtocolError` chỉ đóng kết nối vi phạm. |

---

## BƯỚC 8 — Security Layer (1 điểm)

> **Mục tiêu chấm điểm:** “Encrypt the data payloads (using a standard cryptographic library)
> before sending, and decrypt upon receipt.”

### 8.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 8 là bảo mật. Mỗi lần kết nối, client sinh một cặp khoá **X25519 tạm thời**; server cũng
> sinh một cặp tạm thời. Hai bên trao đổi khoá công khai trong `INITIAL` và `HANDSHAKE`. Server ký
> transcript bằng khoá **Ed25519** dài hạn của mình; client kiểm tra chữ ký và kiểm tra fingerprint
> đã ghim (TOFU) trước khi tin. Sau đó hai bên dùng **HKDF-SHA256** với salt là hai khoá công khai
> để dẫn ra 64 byte, tách thành hai khoá **AES-256-GCM** riêng cho hai chiều. Mỗi gói `DATA` được
> mã hoá bằng AES-GCM; nonce là 4 byte 0 cộng với số thứ tự gói 8 byte; header 13 byte được xác
> thực như **AAD**; cuối gói là tag 16 byte. Gói gửi lại nhận số thứ tự mới nên nonce không bao giờ
> trùng. Mật khẩu lưu bằng PBKDF2 120.000 vòng. File P2P cũng dùng đúng cơ chế này, với khoá
> Ed25519 riêng của từng client; server chỉ công bố fingerprint, người gửi xác minh trước khi gửi.
> Toàn bộ nguyên thuỷ mật mã nằm trong `common/crypto.py`, chỉ dùng thư viện chuẩn `cryptography`,
> không tự viết thuật toán.”

**Nếu chỉ có 30 giây:** “X25519 tạm thời + Ed25519 ký + HKDF ra hai khoá AES-256-GCM; mỗi gói có
nonce là số thứ tự, header làm AAD, tag 16 byte; P2P cũng mã hoá và xác minh fingerprint.”

### 8.2. Demo trên web

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Nhìn dòng trạng thái trong panel phải | “Kết nối ổn định, đang mã hoá AES-256-GCM.” |
| 2 | Mở `source\client_state_8080\known_hosts.json` | Fingerprint server đã ghim, ví dụ `ab12:cd34:...` |
| 3 | So với dòng fingerprint server in lúc khởi động | Giống hệt |
| 4 | Nhập sai mật khẩu ở tab Carol | Báo “Sai mật khẩu”; không vào được |
| 5 | Mở `server_data\users.json` | Chỉ có `pbkdf2$120000$...`; không có mật khẩu |
| 6 | Mở thư mục `client_state_8080` | Có `client_identity.key` (khoá P2P) và `known_hosts.json`; **không mở hay chiếu nội dung khoá riêng** |

**Câu nói:** “Em không chiếu nội dung khoá riêng lên màn hình. Cái được phép công khai là fingerprint
và khoá công khai; khoá riêng chỉ nằm trên máy.”

### 8.3. Wireshark — chứng minh nội dung đã mã hoá

#### 8.3.1. Không đọc được chữ trong gói DATA

**Filter:**

```
udp.port == 9000 && udp.payload[0] == 0x10
```

**Cách tìm gói:**

1. Gửi một tin nhắn có chữ ASCII dễ tìm, ví dụ `hello secret`.
2. Gõ filter trên, Enter. Bấm một gói `10` vừa xuất hiện.
3. Ở khung giữa mở **Data**; ở khung dưới, sau 13 byte header là các byte ngẫu nhiên.
4. Thử tìm chữ trong toàn bộ gói UDP:
   ```
   udp.port == 9000 && frame contains "hello"
   ```
   → **0 packet**.
5. Thử tìm tên đăng nhập:
   ```
   udp.port == 9000 && frame contains "alice"
   ```
   → **0 packet**.

**Câu nói:** “Em vừa gửi chữ ‘hello secret’ và đăng nhập bằng ‘alice’. Wireshark tìm trong toàn bộ
gói UDP cổng 9000 không thấy chuỗi nào. Đó là bằng chứng payload đã được mã hoá trước khi gửi.”

#### 8.3.2. Khoá công khai thì nhìn thấy — đó là chủ ý

**Filter:**

```
udp.port == 9000 && (udp.payload[0] == 0x01 || udp.payload[0] == 0x02)
```

1. Gói `01` dài 57 byte: 13 header + 4 CID + **32 byte khoá công khai X25519**. Khoá công khai không
   phải bí mật; nó dùng để thoả thuận khoá chung.
2. Gói `02` dài 153 byte: 13 + 4 + **32 byte khoá X25519 server** + **32 byte khoá Ed25519 dài hạn**
   + **64 byte chữ ký**. Chữ ký chứng minh server giữ khoá riêng.
3. Wireshark có thể hiển thị các byte này, nhưng **không thể** tính ra khoá phiên vì thiếu khoá riêng
   tạm thời của client/server.

**Câu nói:** “Wireshark thấy khoá công khai và chữ ký — đó là bình thường. Cái không thấy là khoá
riêng và khoá phiên; chúng không bao giờ lên đường truyền.”

#### 8.3.3. Tag xác thực 16 byte

**Cách xem:**

1. Bấm một gói `DATA`. Ghi lại `udp.length` (ví dụ 105).
2. Cấu trúc: 8 byte UDP header + 13 byte header CollabNet + phần mã hoá + 16 byte tag.
3. 16 byte cuối trong khung **Packet Bytes** là tag GCM. Nếu sửa một bit bất kỳ trong phần mã hoá
   hoặc header, bên nhận sẽ tính tag khác và **loại gói**; transport coi như mất gói và gửi lại.
4. Đây là lý do header cũng được bảo vệ: kẻ tấn công không thể sửa số thứ tự gói hay connection id.

**Câu nói:** “16 byte cuối là tag xác thực. Nó không phải chữ ký số, mà là mã xác thực của AES-GCM:
chỉ cần sửa một bit là gói bị loại.”

#### 8.3.4. So sánh với HTTP nội bộ

**Filter:**

```
http.request.method == "POST" && http.request.uri == "/api/login"
```

1. Bạn thấy `user` và `pass` bản rõ trong JSON.
2. Đây là chặng **trình duyệt → gateway** trên cùng máy, qua `127.0.0.1`, không ra LAN.
3. Chặng ra LAN là UDP 9000, đã mã hoá; filter `frame contains "1234"` trên `udp.port == 9000`
   cho 0 gói.
4. Gateway chỉ bind `127.0.0.1`, kiểm tra `Host`, bắt buộc `X-Requested-With` cho POST, và đặt CSP;
   nên trang web lạ không gọi được API này từ trình duyệt.

**Câu nói:** “Đây là điểm dễ gây hiểu nhầm: mật khẩu hiện rõ trong HTTP, nhưng chỉ trong máy. Ra
đường truyền thật, nó nằm trong AUTH đã mã hoá. Nếu thầy/cô muốn, em có thể chỉ filter UDP để
chứng minh không có chuỗi ‘1234’ nào trên cổng 9000.”

#### 8.3.5. P2P cũng mã hoá và xác minh

**Filter:**

```
(udp.payload[0] == 0x01 || udp.payload[0] == 0x02) && udp.port != 9000 && udp.port != 9998
```

1. Khi bắt đầu gửi file, có cặp `01`/`02` giữa hai client.
2. Gói `02` chứa khoá công khai và chữ ký Ed25519 của **client nhận**, không phải server.
3. Alice xác minh fingerprint này khớp với fingerprint server đã công bố trong `PEERS`; lệch thì
   từ chối kết nối (“peer key mismatch”).

**Câu nói:** “File không đi qua server nhưng vẫn được mã hoá đầu-cuối giữa hai client; server chỉ
là người giới thiệu, không giữ khoá phiên P2P.”

#### 8.3.6. Bảng ý nghĩa

| Thành phần | Nhìn thấy trong Wireshark | Ý nghĩa |
|---|---|---|
| Header 13 byte | Loại gói, CID, PN | Định tuyến; được xác thực làm AAD |
| Khoá X25519 | 32 byte trong `01`/`02` | Công khai, dùng thoả thuận khoá |
| Khoá Ed25519 server | 32 byte trong `02` | Danh tính dài hạn, client ghim fingerprint |
| Chữ ký | 64 byte trong `02` | Chứng minh server giữ khoá riêng |
| Payload `10` | Byte ngẫu nhiên | AES-256-GCM, không đọc được |
| Tag | 16 byte cuối | Xác thực toàn vẹn |
| Metadata | IP, cổng, kích thước, thời gian | Vẫn lộ; mã hoá không che giấu metadata |

### 8.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Vì sao AES-GCM? | Mã hoá + xác thực trong một; nhanh, có tăng tốc phần cứng, thư viện chuẩn hỗ trợ. |
| Nonce có trùng không? | Không: mỗi gói một số thứ tự mới, kể cả gói gửi lại; mỗi chiều một khoá riêng. |
| Forward secrecy là gì? | Khoá X25519 chỉ dùng một phiên; lộ khoá dài hạn sau này không giải mã được phiên cũ. |
| Chống MITM thế nào? | Server ký transcript bằng Ed25519; client kiểm tra chữ ký + fingerprint đã ghim. |
| Nếu khoá server đổi? | Client từ chối kết nối và báo “SERVER KEY CHANGED”; muốn tin khoá mới phải xoá `known_hosts.json`. |
| Mật khẩu có an toàn? | PBKDF2 120.000 vòng, muối 16 byte, so sánh hằng thời gian. |
| Sao không dùng TLS? | Đề yêu cầu tự xây giao thức; TLS sẽ che hết và không chứng minh được phần transport. |
| Wireshark thấy gì? | IP, cổng, kích thước, thời gian, CID, PN; không thấy nội dung. |

---
## BƯỚC 9 — HTTP-based UI with Client-side JavaScript (1 điểm)

> **Mục tiêu chấm điểm:** “Build a user-friendly interface that clearly displays incoming messages,
> file transfer progress bars, and active user lists.”

### 9.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 9 là giao diện. Trình duyệt chỉ chạy HTML, CSS và JavaScript thuần; không framework frontend,
> không WebSocket. Mỗi client có một **HTTP gateway** viết tay trên asyncio TCP: nó phục vụ file tĩnh
> theo danh sách trắng, cung cấp API JSON để đăng nhập/gửi tin/upload, và đẩy sự kiện thời gian thực
> bằng **Server-Sent Events** trên `GET /api/events`. SSE là HTTP thường, giữ kết nối mở và gửi các
> dòng `event:` / `data:`; nhờ vậy không cần WebSocket. Giao diện có ba cột: bên trái là danh sách
> cuộc trò chuyện với badge chưa đọc và bản nháp riêng; ở giữa là khung chat với thẻ file có thanh
> tiến trình, tốc độ, thời gian còn lại, nút huỷ/gửi lại/tải về; bên phải là panel đường truyền với
> đồ thị RTT, cửa sổ gửi, số gói mất. Có giao diện sáng/tối, emoji, kéo-thả file, dán ảnh, nhiều
> file cùng lúc, tìm cuộc trò chuyện, và banner khi người nhận offline. Gateway bind `127.0.0.1`,
> kiểm tra header `Host` chống DNS-rebinding, bắt buộc `X-Requested-With` cho POST để chống CSRF,
> đặt CSP và `X-Content-Type-Options: nosniff`. Code ở `client/gateway.py` và `client/web/`.”

**Nếu chỉ có 30 giây:** “UI là HTML/JS thuần; gateway HTTP tự viết phục vụ file tĩnh, REST JSON và
SSE; có tiến trình file, danh sách online, đồ thị RTT/cwnd/loss; bảo vệ loopback + CSP + CSRF.”

### 9.2. Demo trên web — các thành phần giao diện

| # | Bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | Nhìn cột trái | “Cả nhóm”, “Tin nhắn riêng”, tên người, chấm xanh online, badge chưa đọc |
| 2 | Gõ vài chữ vào ô nhập rồi chuyển cuộc trò chuyện | Bản nháp được giữ riêng cho từng cuộc |
| 3 | Gõ vào ô “Tìm cuộc trò chuyện” | Danh sách lọc ngay |
| 4 | Bấm nút mặt trăng/mặt trời | Đổi giao diện sáng/tối |
| 5 | Bấm nút mặt cười, chọn emoji | Emoji chèn vào ô nhập |
| 6 | Gõ một URL `https://...` rồi gửi | Link tự động bấm được |
| 7 | Kéo-thả một file vào khung chat | Hiện lớp phủ “Thả file để gửi”; thả ra thì gửi |
| 8 | Ctrl+V khi đang copy một ảnh | Ảnh được gửi như file, có xem trước thumbnail |
| 9 | Gửi 2 file cùng lúc | Hai thẻ file, hai thanh tiến trình độc lập |
| 10 | Trong lúc gửi, bấm nút X trên thẻ file | Huỷ gửi; thẻ chuyển lỗi “Đã huỷ gửi” |
| 11 | Bấm nút tải xuống trên thẻ file đã nhận | File tải về; ảnh có nút xem trước |
| 12 | Mở panel phải | Đồ thị “Độ trễ”, “Cửa sổ gửi”, “Gói bị mất”, “Thuật toán”, danh sách tệp |
| 13 | Chọn một người đang offline (đã có cuộc trò chuyện) | Banner “đang offline… vẫn được gửi”; ô nhập vẫn bật |
| 14 | Thu nhỏ cửa sổ trình duyệt | Giao diện responsive, có nút quay lại danh sách |

**Câu nói:** “Tất cả những thứ này là JavaScript thuần, không React/Vue, không thư viện UI. Dữ liệu
đến từ SSE; thao tác đi bằng fetch/XHR tới gateway cục bộ.”

### 9.3. Wireshark — giao diện HTTP + SSE

#### 9.3.1. Bật giải mã HTTP cho cổng 8081/8082

Wireshark tự nhận HTTP trên cổng 8080, nhưng có thể chỉ thấy TCP thô trên 8081/8082. Làm một lần:

1. Bấm một gói TCP tới cổng 8081.
2. Menu **Analyze → Decode As…**
3. Bấm dấu **+**, chọn trường **TCP port**, giá trị `8081`, giao thức **HTTP**, bấm OK.
4. Làm lại với `8082`.
5. Bây giờ các filter `http.*` mới khớp.

**Filter tổng quát:**

```
tcp.port >= 8080 && tcp.port <= 8099
```

**Cách tìm gói:**

1. Gõ filter, Enter. Bạn thấy toàn bộ lưu lượng web của 3 client.
2. Để chỉ xem request: dùng filter dưới.
3. Nếu cột Protocol vẫn ghi TCP thay vì HTTP, làm lại bước Decode As.

#### 9.3.2. Danh sách request của giao diện

**Filter:**

```
http.request && tcp.port >= 8080 && tcp.port <= 8099
```

**Bạn sẽ thấy:**

| Request | Ý nghĩa |
|---|---|
| `GET /` | Tải `index.html` |
| `GET /app.js` | JavaScript phía client |
| `GET /style.css` | CSS |
| `GET /fonts/...woff2` | Font Be Vietnam Pro đóng gói sẵn |
| `GET /api/state` | Ảnh chụp trạng thái ban đầu |
| `POST /api/login` | Đăng nhập |
| `GET /api/events` | Kênh SSE realtime |
| `POST /api/send` | Gửi tin nhắn |
| `POST /api/upload` | Gửi file |
| `GET /api/download/...` | Tải file |
| `POST /api/logout` | Đăng xuất |

**Câu nói:** “Đây là toàn bộ API của giao diện. Không có endpoint lạ; mọi thứ đều nằm trong
`client/gateway.py` và đều là HTTP/1.1 thường.”

#### 9.3.3. SSE — kênh đẩy sự kiện thời gian thực

**Filter:**

```
http.request.uri == "/api/events"
```

**Cách tìm gói:**

1. Gõ filter, Enter. Mỗi tab có một request `GET /api/events`.
2. Bấm request của Alice. Ở khung giữa, mở **Hypertext Transfer Protocol**; response có
   `Content-Type: text/event-stream` và `Connection: keep-alive`.
3. Chuột phải → **Follow → TCP Stream**.
4. Trong cửa sổ Follow, chọn **Show data as ASCII**. Bạn thấy các dòng:
   ```
   event: status
   data: {"status":"online",...}

   event: msg
   data: {"id":"...","from":"bob","text":"..."}
   ```
5. Để cửa sổ Follow mở, bấm gửi một tin ở Bob. Dòng `event: msg` mới xuất hiện ngay.

**Câu nói:** “Đây là SSE: server đẩy sự kiện qua một kết nối HTTP mở. Không phải WebSocket, nhưng
vẫn realtime. Thầy/cô thấy dòng `event: msg` xuất hiện đúng lúc em bấm gửi.”

#### 9.3.4. TCP handshake và đặc điểm `Connection: close`

**Filter:**

```
tcp.flags.syn == 1 && tcp.flags.ack == 0 && tcp.port >= 8080 && tcp.port <= 8099
```

1. Mỗi request thường mở một kết nối TCP mới rồi đóng (`Connection: close`), nên thấy nhiều SYN.
2. Riêng SSE giữ một kết nối mở lâu; không thấy SYN lặp lại cho `/api/events`.
3. Đây là lý do đôi khi thấy nhiều “TCP handshake” trong lúc chat — bình thường, không phải lỗi.

#### 9.3.5. Header bảo mật và upload

**Filter upload:**

```
http.request.method == "POST" && http.request.uri == "/api/upload"
```

1. Mở **Hypertext Transfer Protocol**; thấy `Host: 127.0.0.1:8080`,
   `X-Requested-With: collabnet`, `X-To`, `X-Filename`, `X-File-Id`.
2. Response có `Content-Type: application/json`, `Cache-Control: no-store`.
3. Filter response SSE để thấy `Content-Type: text/event-stream`.
4. Filter `http.response.code == 403` khi thử gọi API từ trang lạ (nếu muốn demo CSRF).

**Bảng ý nghĩa:**

| Thành phần | Nhìn thấy gì | Ý nghĩa |
|---|---|---|
| TCP 8080–8099 | Nhiều kết nối ngắn + một kết nối dài | UI cục bộ; `Connection: close` và SSE |
| `GET /api/events` | `text/event-stream`, dòng `data:` | Kênh realtime SSE |
| `POST /api/send` | JSON `to`, `text` | Thao tác người dùng |
| `POST /api/upload` | Header `X-To`, `X-Filename` | Gửi file từ browser → gateway |
| `GET /api/download/...` | `Content-Disposition: attachment` | Tải file đã nhận |
| Header `X-Requested-With` | `collabnet` | Chống CSRF |

### 9.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Vì sao SSE mà không WebSocket? | SSE là HTTP thường, đủ cho một chiều server → client; không cần framework, dễ qua proxy. |
| UI dùng framework gì? | Không; HTML/CSS/JavaScript thuần, `fetch`, `XMLHttpRequest`, `EventSource`. |
| Vì sao UI được dùng HTTP? | Đề yêu cầu UI web; lõi cộng tác vẫn là UDP tự viết. Gateway HTTP do em tự viết, không dùng Flask/Django. |
| Bảo mật UI thế nào? | Bind loopback, kiểm tra Host, `X-Requested-With`, CSP, `nosniff`, `no-store`, lọc tên file. |
| Nhiều kết nối TCP có sao? | Mỗi request ngắn một kết nối; SSE giữ kết nối dài; bình thường với HTTP/1.1. |
| Ảnh xem trước có an toàn? | Chỉ inline cho ảnh, kèm `Content-Security-Policy: sandbox`. |

---

## BƯỚC 10 — Testing & Code Quality (1 điểm)

> **Mục tiêu chấm điểm:** “Code must be cleanly formatted, commented, and pass local network
> simulation tests (connecting from multiple terminal windows).”

### 10.1. Lời thuyết trình (đọc gần như nguyên văn)

> “Bước 10 là kiểm thử và chất lượng mã. Đồ án có **49 test** chia thành nhiều tầng. Tầng unit kiểm
> tra RangeSet, đóng/mở frame, crypto. Tầng transport kiểm tra link sạch, link mất gói với CUBIC và
> BBR, chống head-of-line blocking, flow control, server giả mạo bị từ chối, phát hiện ngắt kết nối.
> Tầng end-to-end dựng server thật và ba client thật trên loopback, gửi tin, gửi file 3 MB, so
> SHA-256, kiểm tra đăng nhập sai, đăng nhập trùng tên, tự kết nối lại. Tầng feature kiểm tra lịch
> sử sau khi đăng xuất, **file chat chung và người offline nhận lại tin/file**, upload bị ngắt không
> để lại file rác. Tầng gateway kiểm tra luồng UI, font, giới hạn upload. Tầng regression giữ các lỗi
> đã sửa: gửi cho peer vừa đóng, hai AUTH chồng nhau, ghi file nguyên tử, tên file Windows. Ngoài ra
> có benchmark CUBIC và BBR ở các mức mất gói 0, 1, 3, 5%, và script `server.reset` để làm sạch dữ
> liệu trước buổi demo. Mã có docstring và chú thích ở các chỗ khó; README có bảng đối chiếu 10 bước
> với vị trí code.”

**Nếu chỉ có 30 giây:** “49 test nhiều tầng, có E2E ba client và link mất gói; benchmark CUBIC/BBR;
code có docstring, README đối chiếu 10 bước.”

### 10.2. Demo trên web và terminal

| # | Lệnh / bấm gì | Kết quả phải thấy |
|---|---|---|
| 1 | `..\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v` | Chạy 49 test; kết thúc `OK` |
| 2 | Nếu không đủ thời gian, chạy `python -m unittest tests.test_e2e tests.test_features -v` | Các test chính của chat/file/offline chạy `ok` |
| 3 | Mở `docs\benchmark.json` | Bảng CUBIC vs BBR |
| 4 | `..\.venv\Scripts\python.exe docs\benchmark.py` (tuỳ chọn) | Chạy lại benchmark, in kết quả |
| 5 | `..\.venv\Scripts\python.exe -m server.reset --dry-run` | In số tài khoản/tin nhắn sẽ xoá, không xoá thật |
| 6 | Mở `README.md` mục 8 | Bảng 10 bước ↔ file code |
| 7 | Mở `tests\test_features.py`, tìm `test_group_file_and_offline_delivery` | Đúng test chứng minh yêu cầu 1 và 2 |

**Câu nói khi mở test offline:** “Đây là test tự động cho đúng yêu cầu số 1 và 2: Bob đăng xuất,
Alice gửi tin riêng, tin chung và hai file; Bob đăng nhập lại, test so SHA-256 của cả file riêng và
file nhóm. Test chạy qua, nên em có thể tự tin demo live.”

### 10.3. Wireshark — số liệu để kết luận

#### 10.3.1. Thống kê file capture

1. Menu **Statistics → Capture File Properties**.
2. Đọc: thời lượng, số gói, average packets/s, kích thước file.
3. Menu **Statistics → Protocol Hierarchy**: thấy UDP chiếm phần lớn; TCP chỉ là UI cục bộ.
4. Menu **Statistics → Conversations → UDP**: thấy hội thoại server (cổng 9000) và các hội thoại P2P
   file (cổng ngẫu nhiên). Đây là bằng chứng định lượng cho kiến trúc.

**Câu nói:** “Trong một file capture duy nhất, thầy/cô thấy cả ba loại: UDP 9000 cho chat, UDP ngẫu
nhiên cho file P2P, và TCP 8080–8099 cho giao diện. Đúng kiến trúc em đã trình bày.”

#### 10.3.2. Expert Information — kiểm tra lỗi gói

1. Menu **Analyze → Expert Information**.
2. Nhóm **Malformed**: phải là **0**. Nếu có, đó là lỗi thật cần sửa.
3. Nhóm **Checksum**: trên Windows có thể báo “incorrect” do **checksum offload** của card mạng.
   Đây là hiện tượng bình thường, không phải app hỏng.
4. Muốn hết nhiễu: **Edit → Preferences → Protocols → IPv4**, bỏ tick “Validate the IPv4 checksum
   if possible”; làm tương tự với **UDP**. Bấm OK.

**Câu nói:** “Wireshark báo checksum sai là do card mạng tính checksum sau khi Wireshark đã chụp;
không phải dữ liệu hỏng. Nhóm Malformed mới là lỗi thật, và đang bằng 0.”

#### 10.3.3. So sánh capture sạch và capture mất gói

1. Lưu capture sạch: **File → Export Specified Packets…**, chọn **All packets**, lưu
   `collabnet_clean.pcapng`.
2. Chạy lại với `--sim-loss 0.05`, bắt một capture khác, lưu `collabnet_lossy.pcapng`.
3. Mở lần lượt hai file; **Statistics → I/O Graph** với filter `udp.port == 9000`.
4. Capture mất gói có ít gói hơn, có khoảng trống PN; nhưng UI vẫn nhận đủ.
5. Nếu dùng `tshark`, đếm nhanh:
   ```bat
   tshark -r collabnet_clean.pcapng -Y "udp.port == 9000" -q -z io,stat,1
   tshark -r collabnet_lossy.pcapng -Y "udp.port == 9000" -q -z io,stat,1
   ```

**Câu nói:** “Hai capture chứng minh: mất gói làm giảm số gói trên dây, nhưng ứng dụng vẫn đúng nhờ
gửi lại. Đây là kết quả kiểm thử định lượng, không chỉ cảm nhận.”

#### 10.3.4. Xuất file nộp kèm

1. **File → Export Specified Packets…**
2. Chọn **Displayed** để chỉ xuất các gói đang lọc (ví dụ toàn bộ `udp.port == 9000`), hoặc **All packets**.
3. Lưu `collabnet_demo.pcapng`; nộp kèm báo cáo nếu giảng viên yêu cầu.
4. Có thể mở lại file bằng Wireshark để chứng minh sau buổi demo.

#### 10.3.5. Bảng benchmark (đọc từ `docs/benchmark.json`)

| Mất gói | CUBIC — thời gian / tốc độ | BBR — thời gian / tốc độ |
|---|---|---|
| 0% | 0,31 s / 51,76 Mbps | 0,42 s / 38,17 Mbps |
| 1% | 2,48 s / 6,46 Mbps | 0,43 s / 37,33 Mbps |
| 3% | 5,76 s / 2,78 Mbps | 0,59 s / 26,89 Mbps |
| 5% | 6,60 s / 2,43 Mbps | 0,55 s / 29,17 Mbps |

**Câu nói:** “Link sạch thì CUBIC nhanh hơn; nhưng khi mất gói, BBR giữ được tốc độ cao hơn nhiều:
ở 5% mất gói, BBR khoảng 29 Mbps so với CUBIC 2,4 Mbps. Vì vậy em cài đặt cả hai và chọn được bằng
tham số `--cc`.”

### 10.4. Câu hỏi giảng viên có thể hỏi

| Câu hỏi | Trả lời ngắn |
|---|---|
| Bao nhiêu test? | 49 test theo README; gồm unit, transport, E2E, feature, gateway, regression. |
| Test có chạy thật không? | E2E dựng server thật + 3 client thật trên loopback, gửi file 3 MB, so SHA-256. |
| Test mất gói ở đâu? | `tests/test_transport.py` và lớp `E2ELossy` (4% loss, 15 ms, BBR). |
| Vì sao có test regression? | Giữ các lỗi đã sửa: gửi cho peer vừa đóng, AUTH chồng nhau, ghi file nguyên tử, tên Windows. |
| Hạn chế của đồ án? | Không resume file, không NAT traversal, history giới hạn 4000 bản ghi, TOFU lần đầu, metadata vẫn lộ. |
| Code quality? | Docstring, chú thích chỗ khó, tên hàm rõ, README đối chiếu 10 bước, không dùng framework mạng. |

---

## KẾT BÀI (đọc nguyên văn)

> “Tóm lại, CollabNet đáp ứng 10 bước của đề bài. Em xin nhấn mạnh hai yêu cầu chức năng: **thứ
> nhất**, khi Bob đăng xuất, Alice vẫn gửi được tin nhắn chung và riêng; Bob đăng nhập lại thì nhận
> đủ cả tin nhắn và file — em đã chứng minh bằng UI, bằng `history.json`, bằng outbox và bằng
> Wireshark (không có gói nào tới Bob khi offline, có gói HISTORY khi Bob vào lại). **Thứ hai**, mọi
> người gửi được file vào chat chung; file đi P2P tới từng người, có SHA-256 kiểm tra, và người
> offline nhận sau. Toàn bộ giao thức chạy trên UDP tự viết, có bắt tay, ACK chọn lọc, điều khiển
> tắc nghẽn, mã hoá AES-256-GCM. Em xin cảm ơn thầy/cô và sẵn sàng trả lời câu hỏi.”

---

## PHỤ LỤC A — Bảng filter copy-paste

| Mục đích | Filter | Kết quả mong đợi |
|---|---|---|
| Tổng quan ứng dụng | `udp.port == 9000 or udp.port == 9998 or (tcp.port >= 8080 and tcp.port <= 8099)` | Chat, beacon, UI |
| Chỉ chat/đăng nhập | `udp.port == 9000` | Gói UDP tới server |
| Chỉ gói chào | `udp.port == 9000 && udp.payload[0] == 0x01` | INITIAL, dài 57 |
| Chỉ gói chào đáp | `udp.port == 9000 && udp.payload[0] == 0x02` | HANDSHAKE, dài 153 |
| Mọi gói dữ liệu | `udp.port == 9000 && udp.payload[0] == 0x10` | DATA mã hoá |
| Gói nhỏ/ACK/PING | `udp.port == 9000 && udp.length < 80` | ACK, PING |
| Gói tin nhắn nhỏ | `udp.port == 9000 && udp.payload[0] == 0x10 && udp.length < 200` | AUTH, MSG ngắn |
| Chiều lên server | `udp.dstport == 9000 && udp.payload[0] == 0x10` | Client → server |
| Chiều xuống client | `udp.srcport == 9000 && udp.payload[0] == 0x10` | Server → client |
| Beacon LAN | `udp.port == 9998` | JSON `svc/port/name` |
| File P2P — chunk lớn | `udp.port != 9000 && udp.port != 9998 && udp.length > 1000` | Hàng nghìn gói ~1200 B |
| Bắt tay P2P | `(udp.payload[0] == 0x01 or udp.payload[0] == 0x02) && udp.port != 9000 && udp.port != 9998` | Cặp 57/153 |
| Chứng minh file không qua server | `udp.port == 9000 && udp.length > 1000` | Rất ít/0 gói |
| Tìm chữ trong chat | `udp.port == 9000 && frame contains "hello"` | 0 gói (đã mã hoá) |
| Tìm tên đăng nhập | `udp.port == 9000 && frame contains "alice"` | 0 gói (đã mã hoá) |
| UI HTTP | `http.request && tcp.port >= 8080 && tcp.port <= 8099` | Danh sách request |
| SSE | `http.request.uri == "/api/events"` | `text/event-stream` |
| Upload | `http.request.method == "POST" && http.request.uri == "/api/upload"` | Header `X-To` |
| Download | `http.request.uri contains "/api/download/"` | File attachment |
| TCP handshake UI | `tcp.flags.syn == 1 && tcp.flags.ack == 0 && tcp.port >= 8080 && tcp.port <= 8099` | Nhiều SYN ngắn |
| Chỉ một client | `udp.port == 9000 && udp.srcport == 50001` | Một hội thoại |
| Chỉ một người nhận | `udp.srcport == 9000 && udp.dstport == 50002` | Gói tới Bob |

---

## PHỤ LỤC B — Lệnh khởi động, reset, kiểm thử

### B.1. Vào thư mục và kiểm tra môi trường

```bat
cd /d "C:\Users\hvy14\Documents\Mạng Máy Tính\Assignment\ASS1\source"
..\.venv\Scripts\python.exe --version
..\.venv\Scripts\python.exe -c "import cryptography; print(cryptography.__version__)"
```

Nếu `.venv` không có, tạo lại theo README:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### B.2. Reset dữ liệu (làm khi server + client đã tắt)

```bat
..\.venv\Scripts\python.exe -m server.reset --dry-run
..\.venv\Scripts\python.exe -m server.reset -y
```

Nếu script từ chối vì cổng bận: tắt hết server + client rồi chạy lại. Chỉ thêm `--force` khi chắc
chắn cổng đó không phải CollabNet.

### B.3. Chạy server

```bat
..\.venv\Scripts\python.exe -m server.server --port 9000
```

Tùy chọn hữu ích:

```bat
..\.venv\Scripts\python.exe -m server.server --port 9000 --cc bbr --sim-loss 0.05 --sim-delay-ms 20
..\.venv\Scripts\python.exe -m server.server --port 9000 --max-file-mb 512
..\.venv\Scripts\python.exe -m server.server --port 9000 --no-beacon
```

### B.4. Chạy 3 client

```bat
..\.venv\Scripts\python.exe -m client.main --ui-port 8080 --server 127.0.0.1:9000 --open
..\.venv\Scripts\python.exe -m client.main --ui-port 8081 --server 127.0.0.1:9000 --open
..\.venv\Scripts\python.exe -m client.main --ui-port 8082 --server 127.0.0.1:9000 --open
```

Mỗi client có thư mục trạng thái riêng `client_state_<port>` chứa `downloads`, `outbox`,
`known_hosts.json`, `client_identity.key`, `received.json`.

### B.5. Kiểm thử và benchmark

```bat
..\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
..\.venv\Scripts\python.exe -m unittest tests.test_features -v
..\.venv\Scripts\python.exe docs\benchmark.py
```

### B.6. Tạo file demo và kiểm tra hash

```bat
..\.venv\Scripts\python.exe -c "import os; open('demo_5mb.bin','wb').write(os.urandom(5*1024*1024))"
certutil -hashfile demo_5mb.bin SHA256
certutil -hashfile client_state_8081\downloads\demo_5mb.bin SHA256
```

### B.7. Tắt sạch

- Trong từng cửa sổ client: Ctrl+C.
- Trong cửa sổ server: Ctrl+C.
- Kiểm tra cổng còn bận:
  ```bat
  netstat -ano | findstr :9000
  netstat -ano | findstr :8080
  ```

---

## PHỤ LỤC C — Định dạng gói và frame (để trả lời câu hỏi sâu)

### C.1. Header 13 byte

| Offset | Kích thước | Trường | Ghi chú |
|---|---|---|---|
| 0 | 1 B | loại gói | `0x01` INITIAL, `0x02` HANDSHAKE, `0x10` DATA |
| 1 | 4 B | connection id đích | big-endian, dùng để định tuyến |
| 5 | 8 B | packet number | big-endian, tăng dần, làm nonce GCM |
| 13 | … | payload | frame đã mã hoá + tag 16 B |

### C.2. Frame bên trong payload

| Frame | Mã | Nội dung |
|---|---|---|
| STREAM | `0x02` | stream_id 4 B, offset 8 B, length 2 B, data |
| STREAM + FIN | `0x03` | như trên, đánh dấu byte cuối stream |
| ACK | `0x04` | largest 8 B, delay 4 B, n 1 B, n × (start 8 B, end 8 B) |
| MAX_STREAM_DATA | `0x05` | stream_id 4 B, max_offset 8 B (credit flow-control) |
| PING | `0x06` | không thân; keep-alive/probe |
| CLOSE | `0x07` | code 2 B, reason_len 2 B, reason |

### C.3. Quy ước stream

| Stream | Ai mở | Dùng cho |
|---|---|---|
| 0 | Client | Điều khiển client → server: AUTH, LIST, FILE_LOG, BYE |
| 1 | Server | Điều khiển server → client: AUTH_OK/FAIL, PEERS, HISTORY, SENT, ERR |
| Chẵn khác | Client | Mỗi tin nhắn một stream mới, FIN ngay |
| Lẻ khác | Server | Mỗi tin nhắn/định tuyến một stream mới |
| Bất kỳ (P2P) | Client gửi | Mỗi file một stream mới trên kết nối P2P |

### C.4. Kích thước gói điển hình

| Gói | `udp.length` | Công thức |
|---|---|---|
| INITIAL | 57 | 8 UDP + 13 header + 36 thân |
| HANDSHAKE | 153 | 8 + 13 + 132 thân |
| DATA nhỏ (ACK/PING) | 38–80 | 8 + 13 + frame + 16 tag |
| DATA chở file | ~1200 | tối đa `MAX_DATAGRAM` 1200 |

---

## PHỤ LỤC D — Checklist 10 điểm (in ra, tick khi demo)

| Bước | Bằng chứng trên web | Bằng chứng Wireshark | File code |
|---|---|---|---|
| 1 | report.pdf kiến trúc; UI | `udp.port == 9000` + cột Kind/CID/PN | `common/packet.py`, `common/protocol.py` |
| 2 | Đăng nhập; toast TOFU | `01`/`02`, dài 57/153; `AUTH` là `10` | `common/transport.py` (`Endpoint.connect`) |
| 3 | 3 user; `users.json`; logout | HTTP `/api/login`; beacon 9998; PEERS | `server/server.py`, `server/users.py` |
| 4 | 3 tab cùng chat | Conversations 3 dòng cổng khác nhau | `common/transport.py`, `server/server.py` |
| 5 | Group/private; Bob offline nhận tin | `/api/send`; fan-out; **0 gói tới cổng Bob**; HISTORY khi vào lại | `client/core.py`, `server/server.py`, `server/history.py` |
| 6 | File nhóm; SHA-256; file offline | P2P >1000 B; 9000 không có gói lớn; `X-To: *`; outbox | `client/core.py` (`send_file`, `_flush_one`) |
| 7 | Tắt/bật server; sim-loss | Khoảng trống PN; PING 4 s; INITIAL mới | `common/transport.py`, `client/core.py` |
| 8 | known_hosts; UI AES-GCM | `10` không đọc được; `frame contains` 0; 57/153 | `common/crypto.py` |
| 9 | UI đầy đủ; SSE realtime | TCP 8080–8099; Follow TCP Stream SSE | `client/gateway.py`, `client/web/` |
| 10 | 49 test; benchmark; reset | Capture Properties; Expert Info; I/O Graph | `tests/`, `docs/` |

---

## PHỤ LỤC E — Xử lý sự cố khi demo

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Wireshark không có card loopback | Npcap cài thiếu loopback | Cài lại Npcap, tick “Support loopback traffic”; mở lại Wireshark |
| Bắt gói nhưng 0 packet | Chọn sai card (Wi-Fi thay vì loopback) | Chọn “Adapter for loopback traffic capture”; bắt lại |
| Không thấy HTTP trên 8081/8082 | Wireshark chưa giải mã cổng đó | Analyze → Decode As → TCP port 8081/8082 → HTTP |
| Filter bị đỏ | Sai cú pháp | Dùng đúng `==`, `&&`, phép hoặc viết bằng chữ `or`; chuỗi phải có nháy kép; `udp.payload[0]`, không `udp[8]` |
| `frame contains "alice"` ra 0 | Đúng như mong đợi | Đó là bằng chứng mã hoá; đừng sửa filter |
| Checksum báo sai | Checksum offload của Windows | Bỏ validate IPv4/UDP checksum trong Preferences |
| Không thấy gói P2P | Chưa gửi file, hoặc firewall chặn | Gửi file; kiểm tra firewall; dùng `udp.port != 9000 && udp.port != 9998` |
| P2P báo lỗi kết nối | Firewall / khác mạng | Cho phép Python trong Windows Firewall; demo cùng máy trước |
| Không đăng nhập được | Sai mật khẩu / dữ liệu cũ | `server.reset -y` khi đã tắt hết; mật khẩu ≥ 4 ký tự |
| Cổng 8080 bận | Client cũ chưa tắt | Tắt cửa sổ cũ; `netstat -ano \| findstr :8080`; đổi cổng |
| Reset bị từ chối | Server/client còn chạy | Tắt hết; chỉ dùng `--force` khi chắc chắn |
| Trình duyệt hiện trang cũ | Cache | Ctrl+F5; hoặc mở tab ẩn danh |
| Bob offline biến mất khỏi danh sách | Chưa từng chat riêng | Chat riêng trước khi logout (xem 0.4) |
| Gửi file nhóm nhưng Bob không thấy ngay | Bob offline | Đúng thiết kế; Bob đăng nhập lại sẽ nhận |
| File nhận bị lỗi | P2P đứt giữa chừng | Gửi lại; kiểm tra SHA-256; xem log client |
| `tshark` không có | Chưa cài hoặc không trong PATH | Dùng GUI; hoặc cài Wireshark kèm tshark |

---

## PHỤ LỤC F — Từ điển nhanh cho người mới

| Thuật ngữ | Nghĩa trong đồ án |
|---|---|
| UDP | Giao thức gửi datagram, không đảm bảo thứ tự/độ tin cậy; đồ án tự xây các thứ đó |
| TCP | Giao thức có kết nối, tin cậy; chỉ dùng cho UI cục bộ, không dùng cho chat/file |
| Datagram | Một gói UDP độc lập |
| Stream | Một luồng byte độc lập trong một kết nối; mỗi tin/mỗi file một stream |
| Handshake | Bắt tay: trao đổi khoá, xác minh danh tính trước khi gửi dữ liệu |
| ACK | Xác nhận đã nhận; trong đồ án là ACK chọn lọc theo khoảng packet number |
| SACK | Selective ACK — báo các khoảng đã nhận để chỉ gửi lại phần thiếu |
| PTO | Probe Timeout — timer gửi lại khi không có ACK |
| RTT | Round-Trip Time — thời gian đi và về |
| cwnd | Congestion window — cửa sổ gửi do điều khiển tắc nghẽn quyết định |
| MTU | Kích thước tối đa một gói trên đường truyền; đồ án dùng datagram tối đa 1200 B |
| P2P | Peer-to-peer — hai client truyền trực tiếp, không qua server |
| SHA-256 | Hàm băm kiểm tra toàn vẹn file |
| AES-256-GCM | Mã hoá đối xứng có xác thực; mỗi gói có nonce và tag |
| X25519 | Trao đổi khoá Diffie-Hellman trên đường cong elliptic |
| Ed25519 | Chữ ký số dùng để chứng minh danh tính server/client |
| HKDF | Hàm dẫn xuất khoá từ bí mật chung |
| PBKDF2 | Hàm băm mật khẩu có muối và nhiều vòng |
| TOFU | Trust On First Use — tin lần đầu, ghim fingerprint |
| SSE | Server-Sent Events — server đẩy sự kiện qua HTTP |
| CSP | Content Security Policy — hạn chế nguồn script/style |
| CID | Connection ID — định danh kết nối trong header |
| PN | Packet Number — số thứ tự gói, làm nonce |
| HoL blocking | Head-of-line blocking — một gói chậm chặn các luồng sau |

---

## PHỤ LỤC G — Ba câu chốt nếu giảng viên chỉ hỏi “tóm tắt đồ án”

1. “CollabNet là chat + gửi file trên **UDP thuần** với transport tự viết kiểu QUIC: đa stream, ACK
   chọn lọc, CUBIC/BBR, AES-256-GCM.”
2. “**Chat và đăng nhập** đi qua server UDP 9000; **file** đi P2P trực tiếp giữa client, server chỉ
   giới thiệu peer và lưu thẻ file.”
3. “**Người offline vẫn nhận được tin nhắn và file**: tin nằm trong `history.json`, byte file nằm
   trong outbox của người gửi; khi người nhận đăng nhập lại, server trả HISTORY và người gửi đẩy
   file P2P. Em có test tự động và capture Wireshark chứng minh.”

---

*Hết kịch bản. Chúc buổi thuyết trình thành công.*
