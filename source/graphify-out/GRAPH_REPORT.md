# Graph Report - source  (2026-11-18)

## Corpus Check
- 28 files · ~38,972 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: .woff2 8, (none) 1, .css 1)

## Summary
- 588 nodes · 1317 edges · 25 communities (14 shown, 11 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 81 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4acc62e6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- json
- Pair
- Endpoint
- Connection
- ClientCore
- transport.py
- Bbr
- E2E
- build_report.py
- core.py
- Gateway
- app.js
- MsgBuffer
- Server
- RangeSet
- server.py
- test_regressions.py
- SendStream
- TransportTests
- test_gateway.py
- os
- RecvStream

## God Nodes (most connected - your core abstractions)
1. `ClientCore` - 56 edges
2. `Connection` - 45 edges
3. `Endpoint` - 33 edges
4. `Server` - 30 edges
5. `Gateway` - 24 edges
6. `connectEvents()` - 20 edges
7. `Pair` - 19 edges
8. `RangeSet` - 16 edges
9. `E2E` - 16 edges
10. `pack()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `7. Đối chiếu yêu cầu đề bài` --references--> `Session`  [INFERRED]
  README.md → server/server.py
- `E2E` --uses--> `AuthError`  [INFERRED]
  tests/test_e2e.py → client/core.py
- `ReconnectTests` --uses--> `AuthError`  [INFERRED]
  tests/test_regressions.py → client/core.py
- `ReconnectTests` --uses--> `AuthRejected`  [INFERRED]
  tests/test_regressions.py → client/core.py
- `ClientCore` --uses--> `Endpoint`  [INFERRED]
  client/core.py → common/transport.py

## Import Cycles
- None detected.

## Communities (25 total, 11 thin omitted)

### Community 0 - "json"
Cohesion: 0.18
Nodes (3): atomic_write_json(), atomic_write_text(), FsUtilTests

### Community 2 - "Endpoint"
Cohesion: 0.06
Nodes (12): derive_keys(), hash_password(), load_or_create_identity(), new_ephemeral(), PacketCipher, public_bytes(), sign(), transcript() (+4 more)

### Community 4 - "ClientCore"
Cohesion: 0.06
Nodes (9): ClientCore, verify(), progress(), check(), fingerprint(), pack(), ReconnectTests, ServerFixture (+1 more)

### Community 5 - "transport.py"
Cohesion: 0.18
Nodes (7): decode_frames(), enc_ack(), enc_close(), enc_max_stream_data(), enc_ping(), enc_stream(), UnitTests

### Community 6 - "Bbr"
Cohesion: 0.08
Nodes (6): Bbr, CongestionControl, Cubic, make_cc(), RateSample, BbrWindowedMaxTests

### Community 7 - "E2E"
Cohesion: 0.10
Nodes (5): chunked(), Collector, E2E, E2ELossy, FeatureTests

### Community 8 - "build_report.py"
Cohesion: 0.11
Nodes (6): architecture(), arrow(), box(), build(), make_diagrams(), sequence()

### Community 10 - "Gateway"
Cohesion: 0.13
Nodes (3): Gateway, HttpError, GatewayHardeningTests

### Community 11 - "app.js"
Cohesion: 0.08
Nodes (67): addItem(), api(), appendRow(), applyTheme(), autosize(), avatar(), buildFile(), buildRow() (+59 more)

### Community 12 - "MsgBuffer"
Cohesion: 0.10
Nodes (11): MsgBuffer, 1. Yêu cầu, 2. Chạy server (Terminal 1), 3. Chạy client (mỗi người dùng một terminal), 4. Mô phỏng mạng xấu (kiểm thử), 5. Kiểm thử tự động, 6. Cấu trúc mã nguồn, 7. Đối chiếu yêu cầu đề bài (+3 more)

### Community 16 - "Server"
Cohesion: 0.07
Nodes (5): ProtocolError, HistoryStore, Server, UserStore, UserStoreTests

### Community 18 - "server.py"
Cohesion: 0.23
Nodes (4): amain(), main(), amain(), main()

### Community 19 - "test_regressions.py"
Cohesion: 0.16
Nodes (3): AuthError, AuthRejected, ProtocolTests

### Community 22 - "test_gateway.py"
Cohesion: 0.31
Nodes (3): GatewayTests, http(), jpost()

## Knowledge Gaps
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ClientCore` connect `ClientCore` to `Endpoint`, `E2E`, `core.py`, `Gateway`, `MsgBuffer`, `server.py`, `test_regressions.py`, `test_gateway.py`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ClientCore` (e.g. with `Endpoint` and `E2E`) actually correct?**
  _`ClientCore` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `Endpoint` be split into smaller, more focused modules?**
  _Cohesion score 0.05889724310776942 - nodes in this community are weakly interconnected._
- **Why does `Endpoint` connect `Endpoint` to `Pair`, `ClientCore`, `transport.py`, `E2E`, `core.py`, `Server`, `server.py`, `test_regressions.py`, `TransportTests`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Connection` (e.g. with `RateSample` and `RangeSet`) actually correct?**
  _`Connection` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Connection` be split into smaller, more focused modules?**
  _Cohesion score 0.08771929824561403 - nodes in this community are weakly interconnected._
- **Why does `Connection` connect `Connection` to `Endpoint`, `transport.py`, `Bbr`, `RangeSet`, `SendStream`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._