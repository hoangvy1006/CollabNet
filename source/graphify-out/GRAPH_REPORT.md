# Graph Report - source  (2026-11-24)

## Corpus Check
- 33 files · ~83,951 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: .woff2 8, (none) 1, .css 1)

## Summary
- 816 nodes · 1714 edges · 39 communities (31 shown, 8 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f33fbc3f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- core.py
- Bộ lọc Wireshark cho buổi demo CollabNet
- Endpoint
- Connection
- ClientCore
- pack
- Bbr
- E2E
- build_report.py
- ServerFixture
- Gateway
- app.js
- MsgBuffer
- test_e2e.py
- Server
- HistoryStore
- 6.3. Wireshark — chứng minh file đi P2P, không qua server
- 8.3. Wireshark — chứng minh nội dung đã mã hoá
- ProtocolError
- TransportTests
- 0. TRƯỚC KHI VÀO PHÒNG THI
- 9.3. Wireshark — giao diện HTTP + SSE
- 5.3. Wireshark — định tuyến và bằng chứng offline
- PHỤ LỤC B — Lệnh khởi động, reset, kiểm thử
- KỊCH BẢN THUYẾT TRÌNH & DEMO — CollabNet
- BƯỚC 1 — Setup & Protocol Design (1 điểm)
- BƯỚC 2 — Basic Client-Server Handshake (1 điểm)
- PHỤ LỤC C — Định dạng gói và frame (để trả lời câu hỏi sâu)
- UserStore
- test_regressions.py
- server.py
- os
- test_review_fixes.py
- 7.3. Wireshark — nhìn dấu vết mất gói và phục hồi
- benchmark.py

## God Nodes (most connected - your core abstractions)
1. `ClientCore` - 79 edges
2. `Connection` - 46 edges
3. `Server` - 38 edges
4. `Endpoint` - 35 edges
5. `pack()` - 24 edges
6. `Gateway` - 24 edges
7. `MsgBuffer` - 23 edges
8. `connectEvents()` - 21 edges
9. `KỊCH BẢN THUYẾT TRÌNH & DEMO — CollabNet` - 20 edges
10. `Pair` - 19 edges

## Surprising Connections (you probably didn't know these)
- `7.1. Lời thuyết trình (đọc gần như nguyên văn)` --references--> `ProtocolError`  [INFERRED]
  docs/presentation_script.md → common/protocol.py
- `7.4. Câu hỏi giảng viên có thể hỏi` --references--> `ProtocolError`  [INFERRED]
  docs/presentation_script.md → common/protocol.py
- `4.1. Lời thuyết trình (đọc gần như nguyên văn)` --references--> `Session`  [INFERRED]
  docs/presentation_script.md → server/server.py
- `3.1. Lời thuyết trình (đọc gần như nguyên văn)` --references--> `Server`  [INFERRED]
  docs/presentation_script.md → server/server.py
- `4.1. Lời thuyết trình (đọc gần như nguyên văn)` --references--> `Connection`  [INFERRED]
  docs/presentation_script.md → common/transport.py

## Import Cycles
- None detected.

## Communities (39 total, 8 thin omitted)

### Community 0 - "core.py"
Cohesion: 0.14
Nodes (4): AuthError, AuthRejected, safe_filename(), ProtocolTests

### Community 1 - "Bộ lọc Wireshark cho buổi demo CollabNet"
Cohesion: 0.12
Nodes (15): 0. Bản đồ cổng của chương trình (dùng để đặt filter), 10. Coloring rules gợi ý (View → Coloring Rules), 11. Capture filter (ô "Capture filter", hoặc `tshark -f`), 12. Lệnh tshark theo từng "cảnh" demo (tuỳ chọn), 13. Lưu ý khi trình bày (rất nên nói trước lớp), 1. Toàn cảnh buổi demo (mở đầu), 2. Bắt tay transport (X25519 + Ed25519) — Bước 2 của đề bài, 3. Đăng nhập / đăng ký (+7 more)

### Community 2 - "Endpoint"
Cohesion: 0.06
Nodes (16): derive_keys(), load_or_create_identity(), new_ephemeral(), PacketCipher, public_bytes(), sign(), transcript(), verify() (+8 more)

### Community 3 - "Connection"
Cohesion: 0.05
Nodes (5): RangeSet, Connection, SendStream, SentPacket, UnitTests

### Community 4 - "ClientCore"
Cohesion: 0.05
Nodes (5): ClientCore, verify(), progress(), check(), fingerprint()

### Community 5 - "pack"
Cohesion: 0.24
Nodes (3): pack(), tcp_exchange(), TcpHandshakeTests

### Community 6 - "Bbr"
Cohesion: 0.05
Nodes (13): Bbr, CongestionControl, Cubic, make_cc(), RateSample, decode_frames(), enc_ack(), enc_close() (+5 more)

### Community 7 - "E2E"
Cohesion: 0.07
Nodes (14): 10.1. Lời thuyết trình (đọc gần như nguyên văn), 10.2. Demo trên web và terminal, 10.3.1. Thống kê file capture, 10.3.2. Expert Information — kiểm tra lỗi gói, 10.3.3. So sánh capture sạch và capture mất gói, 10.3.4. Xuất file nộp kèm, 10.3.5. Bảng benchmark (đọc từ `docs/benchmark.json`), 10.3. Wireshark — số liệu để kết luận (+6 more)

### Community 8 - "build_report.py"
Cohesion: 0.07
Nodes (14): build(), Doc, inline(), is_separator(), make_table(), parse(), split_table_row(), wrap_code() (+6 more)

### Community 9 - "ServerFixture"
Cohesion: 0.18
Nodes (3): ReconnectTests, ServerFixture, ServerRobustnessTests

### Community 10 - "Gateway"
Cohesion: 0.10
Nodes (6): Gateway, HttpError, GatewayTests, http(), jpost(), GatewayHardeningTests

### Community 11 - "app.js"
Cohesion: 0.08
Nodes (68): addItem(), api(), appendRow(), applyTheme(), asItem(), autosize(), avatar(), buildFile() (+60 more)

### Community 12 - "MsgBuffer"
Cohesion: 0.10
Nodes (13): exchange(), MsgBuffer, 3.1. Lời thuyết trình (đọc gần như nguyên văn), 3.2. Demo trên web, 3.3.1. Bản rõ của thao tác đăng nhập (chỉ trên loopback), 3.3.2. AUTH đã mã hoá trên UDP, 3.3.3. Beacon tìm server trong LAN (bản rõ có chủ ý), 3.3.4. Presence khi có người ra/vào (+5 more)

### Community 15 - "test_e2e.py"
Cohesion: 0.15
Nodes (3): hash_password(), chunked(), ReviewFixTests

### Community 18 - "6.3. Wireshark — chứng minh file đi P2P, không qua server"
Cohesion: 0.18
Nodes (11): 6.1. Lời thuyết trình (đọc gần như nguyên văn), 6.2. Tạo file demo và demo gửi file, 6.3.1. Tìm luồng file P2P, 6.3.2. Chứng minh file **không** đi qua server, 6.3.3. Bắt tay P2P trước khi truyền, 6.3.4. Phía giao diện web (bản rõ trong máy), 6.3.5. Bằng chứng file gửi cho Bob offline, 6.3.6. Bảng ý nghĩa (+3 more)

### Community 19 - "8.3. Wireshark — chứng minh nội dung đã mã hoá"
Cohesion: 0.18
Nodes (11): 8.1. Lời thuyết trình (đọc gần như nguyên văn), 8.2. Demo trên web, 8.3.1. Không đọc được chữ trong gói DATA, 8.3.2. Khoá công khai thì nhìn thấy — đó là chủ ý, 8.3.3. Tag xác thực 16 byte, 8.3.4. So sánh với HTTP nội bộ, 8.3.5. P2P cũng mã hoá và xác minh, 8.3.6. Bảng ý nghĩa (+3 more)

### Community 20 - "ProtocolError"
Cohesion: 0.22
Nodes (8): ProtocolError, 7.1. Lời thuyết trình (đọc gần như nguyên văn), 7.2.1. Tắt server rồi bật lại, 7.2.2. Đóng client đột ngột, 7.2.3. Mô phỏng mạng mất gói, 7.2. Demo trên web — mất server, tự kết nối lại, mất gói, 7.4. Câu hỏi giảng viên có thể hỏi, BƯỚC 7 — Network Resilience & Error Handling (1 điểm)

### Community 21 - "TransportTests"
Cohesion: 0.14
Nodes (3): TransportInternalsTests, Pair, TransportTests

### Community 22 - "0. TRƯỚC KHI VÀO PHÒNG THI"
Cohesion: 0.20
Nodes (10): 0.1. Cần có trên máy, 0.2. Sơ đồ cổng — thuộc lòng 4 dòng này, 0.3. Khởi động trong 5 lệnh (cách nhanh nhất), 0.4. Đăng nhập 3 người dùng (làm một lần, dùng cho cả buổi), 0.5. Bố cục màn hình khi trình bày, 0.6. Cách đọc một gói CollabNet (13 byte header) — hiểu một lần, dùng cả buổi, 0.7. Sáu thao tác Wireshark dùng đi dùng lại, 0.8. Lịch trình 18 phút (+2 more)

### Community 23 - "9.3. Wireshark — giao diện HTTP + SSE"
Cohesion: 0.20
Nodes (10): 9.1. Lời thuyết trình (đọc gần như nguyên văn), 9.2. Demo trên web — các thành phần giao diện, 9.3.1. Bật giải mã HTTP cho cổng 8081/8082, 9.3.2. Danh sách request của giao diện, 9.3.3. SSE — kênh đẩy sự kiện thời gian thực, 9.3.4. TCP handshake và đặc điểm `Connection: close`, 9.3.5. Header bảo mật và upload, 9.3. Wireshark — giao diện HTTP + SSE (+2 more)

### Community 25 - "5.3. Wireshark — định tuyến và bằng chứng offline"
Cohesion: 0.25
Nodes (8): 5.2. Demo trên web — chat chung, chat riêng, offline, 5.3.1. Mỗi tin nhắn là một request UI riêng, 5.3.2. Chiều client → server và server → client, 5.3.3. Bằng chứng mạnh nhất: Bob offline thì **không có gói nào** tới Bob, 5.3.4. Bảng ý nghĩa, 5.3. Wireshark — định tuyến và bằng chứng offline, 5.4. Câu hỏi giảng viên có thể hỏi, BƯỚC 5 — Time-sensitive Streaming & Message Routing (1 điểm)

### Community 26 - "PHỤ LỤC B — Lệnh khởi động, reset, kiểm thử"
Cohesion: 0.25
Nodes (8): B.1. Vào thư mục và kiểm tra môi trường, B.2. Reset dữ liệu (làm khi server + client đã tắt), B.3. Chạy server, B.4. Chạy 3 client, B.5. Kiểm thử và benchmark, B.6. Tạo file demo và kiểm tra hash, B.7. Tắt sạch, PHỤ LỤC B — Lệnh khởi động, reset, kiểm thử

### Community 27 - "KỊCH BẢN THUYẾT TRÌNH & DEMO — CollabNet"
Cohesion: 0.29
Nodes (6): KẾT BÀI (đọc nguyên văn), KỊCH BẢN THUYẾT TRÌNH & DEMO — CollabNet, PHỤ LỤC A — Bảng filter copy-paste, PHỤ LỤC E — Xử lý sự cố khi demo, PHỤ LỤC F — Từ điển nhanh cho người mới, PHỤ LỤC G — Ba câu chốt nếu giảng viên chỉ hỏi “tóm tắt đồ án”

### Community 28 - "BƯỚC 1 — Setup & Protocol Design (1 điểm)"
Cohesion: 0.40
Nodes (5): 1.1. Lời thuyết trình (đọc gần như nguyên văn), 1.2. Demo trên web, 1.3. Wireshark — chứng minh cấu trúc gói, 1.4. Câu hỏi giảng viên có thể hỏi, BƯỚC 1 — Setup & Protocol Design (1 điểm)

### Community 29 - "BƯỚC 2 — Basic Client-Server Handshake (1 điểm)"
Cohesion: 0.40
Nodes (5): 2.1. Lời thuyết trình (đọc gần như nguyên văn), 2.2. Demo trên web, 2.3. Wireshark — bắt tay và ACK, 2.4. Câu hỏi giảng viên có thể hỏi, BƯỚC 2 — Basic Client-Server Handshake (1 điểm)

### Community 30 - "PHỤ LỤC C — Định dạng gói và frame (để trả lời câu hỏi sâu)"
Cohesion: 0.40
Nodes (5): C.1. Header 13 byte, C.2. Frame bên trong payload, C.3. Quy ước stream, C.4. Kích thước gói điển hình, PHỤ LỤC C — Định dạng gói và frame (để trả lời câu hỏi sâu)

### Community 32 - "test_regressions.py"
Cohesion: 0.24
Nodes (3): atomic_write_json(), atomic_write_text(), FsUtilTests

### Community 33 - "server.py"
Cohesion: 0.20
Nodes (4): amain(), main(), amain(), main()

### Community 34 - "os"
Cohesion: 0.19
Nodes (6): _client_state_ports(), _counts(), _load_json(), main(), _parse_ports(), _port_busy()

### Community 35 - "test_review_fixes.py"
Cohesion: 0.16
Nodes (5): Beacon, discover(), _recvfrom(), DiscoveryTests, RateSampleTests

### Community 36 - "7.3. Wireshark — nhìn dấu vết mất gói và phục hồi"
Cohesion: 0.33
Nodes (6): 7.3.1. Khoảng trống packet number, 7.3.2. Keep-alive khi rảnh, 7.3.3. Bắt tay lại sau khi server khởi động lại, 7.3.4. Đăng xuất êm, 7.3.5. Bảng ý nghĩa, 7.3. Wireshark — nhìn dấu vết mất gói và phục hồi

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ClientCore` connect `ClientCore` to `core.py`, `server.py`, `test_regressions.py`, `pack`, `E2E`, `ServerFixture`, `Gateway`, `MsgBuffer`, `test_e2e.py`, `ProtocolError`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `ClientCore` (e.g. with `MsgBuffer` and `ProtocolError`) actually correct?**
  _`ClientCore` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `core.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13970588235294118 - nodes in this community are weakly interconnected._
- **Why does `KỊCH BẢN THUYẾT TRÌNH & DEMO — CollabNet` connect `KỊCH BẢN THUYẾT TRÌNH & DEMO — CollabNet` to `Endpoint`, `E2E`, `MsgBuffer`, `6.3. Wireshark — chứng minh file đi P2P, không qua server`, `8.3. Wireshark — chứng minh nội dung đã mã hoá`, `ProtocolError`, `0. TRƯỚC KHI VÀO PHÒNG THI`, `9.3. Wireshark — giao diện HTTP + SSE`, `5.3. Wireshark — định tuyến và bằng chứng offline`, `PHỤ LỤC B — Lệnh khởi động, reset, kiểm thử`, `BƯỚC 1 — Setup & Protocol Design (1 điểm)`, `BƯỚC 2 — Basic Client-Server Handshake (1 điểm)`, `PHỤ LỤC C — Định dạng gói và frame (để trả lời câu hỏi sâu)`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `Server` (e.g. with `3.1. Lời thuyết trình (đọc gần như nguyên văn)` and `Beacon`) actually correct?**
  _`Server` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `Bộ lọc Wireshark cho buổi demo CollabNet` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `Endpoint` connect `Endpoint` to `core.py`, `server.py`, `test_regressions.py`, `test_review_fixes.py`, `ClientCore`, `Connection`, `Bbr`, `E2E`, `ServerFixture`, `test_e2e.py`, `TransportTests`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._