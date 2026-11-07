# Graph Report - Source Code  (2026-11-06)

## Corpus Check
- 23 files · ~18,173 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: .css 1)

## Summary
- 400 nodes · 870 edges · 16 communities (11 shown, 5 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 59 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `829e6659`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- Endpoint
- crypto.py
- Connection
- ClientCore
- transport.py
- Bbr
- RangeSet
- build_report.py
- Server
- Gateway
- app.js
- CollabNet — Distributed Streaming-based Client-Server Collaboration Application

## God Nodes (most connected - your core abstractions)
1. `Connection` - 44 edges
2. `ClientCore` - 38 edges
3. `Endpoint` - 27 edges
4. `Server` - 26 edges
5. `Gateway` - 20 edges
6. `MsgBuffer` - 17 edges
7. `RangeSet` - 15 edges
8. `Pair` - 15 edges
9. `SendStream` - 14 edges
10. `E2E` - 13 edges

## Surprising Connections (you probably didn't know these)
- `7. Đối chiếu yêu cầu đề bài` --references--> `Session`  [INFERRED]
  README.md → server/server.py
- `E2E` --uses--> `AuthError`  [INFERRED]
  tests/test_e2e.py → client/core.py
- `ClientCore` --uses--> `ProtocolError`  [INFERRED]
  client/core.py → common/protocol.py
- `ClientCore` --uses--> `Endpoint`  [INFERRED]
  client/core.py → common/transport.py
- `E2E` --uses--> `ClientCore`  [INFERRED]
  tests/test_e2e.py → client/core.py

## Import Cycles
- None detected.

## Communities (16 total, 5 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.09
Nodes (12): amain(), main(), discover(), safe_filename(), main(), run(), amain(), main() (+4 more)

### Community 1 - "Endpoint"
Cohesion: 0.06
Nodes (7): load_or_create_identity(), Endpoint, Collector, E2E, E2ELossy, Pair, TransportTests

### Community 2 - "crypto.py"
Cohesion: 0.08
Nodes (12): derive_keys(), fingerprint(), hash_password(), new_ephemeral(), PacketCipher, public_bytes(), sign(), transcript() (+4 more)

### Community 4 - "ClientCore"
Cohesion: 0.10
Nodes (6): AuthError, ClientCore, progress(), check(), MsgBuffer, StreamState

### Community 5 - "transport.py"
Cohesion: 0.12
Nodes (8): RateSample, decode_frames(), enc_ack(), enc_close(), enc_max_stream_data(), enc_ping(), enc_stream(), RecvStream

### Community 6 - "Bbr"
Cohesion: 0.10
Nodes (4): Bbr, CongestionControl, Cubic, make_cc()

### Community 7 - "RangeSet"
Cohesion: 0.13
Nodes (3): RangeSet, SendStream, UnitTests

### Community 8 - "build_report.py"
Cohesion: 0.12
Nodes (6): architecture(), arrow(), box(), build(), make_diagrams(), sequence()

### Community 9 - "Server"
Cohesion: 0.21
Nodes (4): pack(), ProtocolError, Relay, Server

### Community 11 - "app.js"
Cohesion: 0.24
Nodes (18): addMessage(), appendLog(), connectEvents(), el(), fmtSize(), fmtTime(), H, onLogin() (+10 more)

### Community 12 - "CollabNet — Distributed Streaming-based Client-Server Collaboration Application"
Cohesion: 0.18
Nodes (9): 1. Yêu cầu, 2. Chạy server (Terminal 1), 3. Chạy client (mỗi người dùng một terminal), 4. Mô phỏng mạng xấu (kiểm thử), 5. Kiểm thử tự động, 6. Cấu trúc mã nguồn, 7. Đối chiếu yêu cầu đề bài, CollabNet — Distributed Streaming-based Client-Server Collaboration Application (+1 more)

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Connection` connect `Connection` to `Endpoint`, `crypto.py`, `transport.py`, `Bbr`, `RangeSet`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Connection` (e.g. with `RateSample` and `RangeSet`) actually correct?**
  _`Connection` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `server.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0946938775510204 - nodes in this community are weakly interconnected._
- **Why does `Endpoint` connect `Endpoint` to `server.py`, `crypto.py`, `ClientCore`, `transport.py`, `Server`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ClientCore` (e.g. with `MsgBuffer` and `ProtocolError`) actually correct?**
  _`ClientCore` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `Endpoint` be split into smaller, more focused modules?**
  _Cohesion score 0.06377551020408163 - nodes in this community are weakly interconnected._
- **Why does `ClientCore` connect `ClientCore` to `server.py`, `Server`, `Gateway`, `Endpoint`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._