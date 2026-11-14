# Graph Report - source  (2026-11-14)

## Corpus Check
- 28 files · ~29,995 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: .woff2 8, (none) 1, .css 1)

## Summary
- 531 nodes · 1224 edges · 20 communities (14 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 75 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `411627c6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- Pair
- Endpoint
- Connection
- ClientCore
- transport.py
- Bbr
- E2E
- build_report.py
- crypto.py
- Gateway
- app.js
- Server
- load_or_create_identity
- PacketCipher
- ._on_handshake

## God Nodes (most connected - your core abstractions)
1. `ClientCore` - 45 edges
2. `Connection` - 45 edges
3. `Endpoint` - 32 edges
4. `Server` - 31 edges
5. `Gateway` - 23 edges
6. `connectEvents()` - 20 edges
7. `Pair` - 18 edges
8. `RangeSet` - 16 edges
9. `E2E` - 15 edges
10. `pack()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `7. Đối chiếu yêu cầu đề bài` --references--> `Session`  [INFERRED]
  README.md → server/server.py
- `E2E` --uses--> `AuthError`  [INFERRED]
  tests/test_e2e.py → client/core.py
- `ClientCore` --uses--> `Endpoint`  [INFERRED]
  client/core.py → common/transport.py
- `E2E` --uses--> `ClientCore`  [INFERRED]
  tests/test_e2e.py → client/core.py
- `GatewayTests` --uses--> `ClientCore`  [INFERRED]
  tests/test_gateway.py → client/core.py

## Import Cycles
- None detected.

## Communities (20 total, 6 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.09
Nodes (10): amain(), main(), Beacon, discover(), safe_filename(), main(), run(), amain() (+2 more)

### Community 1 - "Pair"
Cohesion: 0.14
Nodes (3): TransportInternalsTests, Pair, TransportTests

### Community 3 - "Connection"
Cohesion: 0.06
Nodes (4): RangeSet, Connection, SendStream, SentPacket

### Community 4 - "ClientCore"
Cohesion: 0.07
Nodes (9): AuthError, AuthRejected, ClientCore, progress(), check(), pack(), ReconnectTests, ServerFixture (+1 more)

### Community 5 - "transport.py"
Cohesion: 0.14
Nodes (8): decode_frames(), enc_ack(), enc_close(), enc_max_stream_data(), enc_ping(), enc_stream(), RecvStream, UnitTests

### Community 6 - "Bbr"
Cohesion: 0.05
Nodes (11): Bbr, CongestionControl, Cubic, make_cc(), RateSample, atomic_write_json(), atomic_write_text(), BbrWindowedMaxTests (+3 more)

### Community 7 - "E2E"
Cohesion: 0.13
Nodes (5): chunked(), Collector, E2E, E2ELossy, FeatureTests

### Community 8 - "build_report.py"
Cohesion: 0.12
Nodes (6): architecture(), arrow(), box(), build(), make_diagrams(), sequence()

### Community 9 - "crypto.py"
Cohesion: 0.20
Nodes (3): fingerprint(), hash_password(), verify_password()

### Community 10 - "Gateway"
Cohesion: 0.12
Nodes (6): Gateway, HttpError, GatewayTests, http(), jpost(), GatewayHardeningTests

### Community 11 - "app.js"
Cohesion: 0.08
Nodes (67): addItem(), api(), appendRow(), applyTheme(), autosize(), avatar(), buildFile(), buildRow() (+59 more)

### Community 12 - "Server"
Cohesion: 0.07
Nodes (13): MsgBuffer, ProtocolError, 1. Yêu cầu, 2. Chạy server (Terminal 1), 3. Chạy client (mỗi người dùng một terminal), 4. Mô phỏng mạng xấu (kiểm thử), 5. Kiểm thử tự động, 6. Cấu trúc mã nguồn (+5 more)

### Community 16 - "load_or_create_identity"
Cohesion: 0.25
Nodes (4): load_or_create_identity(), public_bytes(), sign(), UserStore

### Community 18 - "._on_handshake"
Cohesion: 0.33
Nodes (3): derive_keys(), transcript(), verify()

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Connection` connect `Connection` to `Endpoint`, `._on_handshake`, `transport.py`, `Bbr`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ClientCore` (e.g. with `Endpoint` and `E2E`) actually correct?**
  _`ClientCore` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `server.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08985507246376812 - nodes in this community are weakly interconnected._
- **Why does `Endpoint` connect `Endpoint` to `server.py`, `Pair`, `ClientCore`, `transport.py`, `Bbr`, `E2E`, `Server`, `load_or_create_identity`, `._on_handshake`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Connection` (e.g. with `RateSample` and `RangeSet`) actually correct?**
  _`Connection` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Pair` be split into smaller, more focused modules?**
  _Cohesion score 0.14210526315789473 - nodes in this community are weakly interconnected._
- **Why does `ClientCore` connect `ClientCore` to `server.py`, `Endpoint`, `Bbr`, `E2E`, `Gateway`, `Server`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._