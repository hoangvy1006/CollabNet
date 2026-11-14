# Graph Report - Assignment 1 - Distributed Streaming-based Client-Server Collaboration Application  (2026-11-06)

## Corpus Check
- Corpus is ~85,200 words (code, assignment brief, project report, diagrams, and eight textbook chapters). The first detect pass cached PDF word counts as 0 before the PDF reader was installed; this line replaces that stale ~17,041-word warning.

## Summary
- 968 nodes · 1821 edges · 42 communities (31 shown, 11 thin omitted)
- Extraction: 89% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 186 edges (avg confidence: 0.86)
- Token cost: 81,600 input · 42,000 output

## Community Hubs (Navigation)
- Chapter 1 Internet Basics
- Chapter 7 Wireless Mobile
- Client Core Session
- Chapter 2 Application Layer
- Chapter 6 Link Layer
- Chapter 3 Transport TCP
- Crypto Packet Cipher
- Chapter 4 Data Plane
- Chapter 5 Routing Control
- Chapter 8 Network Security
- Connection Send Path
- CUBIC and BBR
- CollabNet UI Screenshot
- Packet Wire Format
- Report Figure Generation
- Browser App Script
- Server Relay Routing
- Process Entry Points
- Protocol and Benchmark
- File Transfer Sequence
- Password and Identity
- Handshake and Keys
- Assignment Requirements
- HTTP Gateway Routes
- Message Sequence Diagram
- Web UI and Messages
- Architecture Requirements
- Range Set Tests
- Architecture Diagram
- LAN UDP Discovery
- Gateway HTTP Tests
- Send Stream Window
- Login and Discovery UI
- Receive Stream Reassembly
- QUIC-Style Reliability
- Flow Control Frames
- Loss Benchmark Tests
- Rate Sample
- Unicast Message Title

## God Nodes (most connected - your core abstractions)
1. `Connection` - 43 edges
2. `ClientCore` - 37 edges
3. `Endpoint` - 27 edges
4. `Server` - 26 edges
5. `Gateway` - 19 edges
6. `TCP (Transmission Control Protocol)` - 19 edges
7. `Assignment project brief` - 18 edges
8. `MsgBuffer` - 17 edges
9. `RangeSet` - 15 edges
10. `Pair` - 15 edges

## Surprising Connections (you probably didn't know these)
- `LAN UDP beacon discovery` --semantically_similar_to--> `Beacon and PEERS presence`  [INFERRED] [semantically similar]
  Source Code/README.md → graphify-out/converted/report_337b3c07.md
- `common/protocol.py` --semantically_similar_to--> `Length-prefixed JSON messages`  [INFERRED] [semantically similar]
  Source Code/README.md → graphify-out/converted/report_337b3c07.md
- `Streaming broadcast and unicast messaging` --semantically_similar_to--> `Per-message stream routing`  [INFERRED] [semantically similar]
  graphify-out/converted/Assignment 1 - Distributed Streaming-based Client-Server Collaboration Application_1fd07668.md → Source Code/README.md
- `Per-message stream routing` --semantically_similar_to--> `Per-stream ordering`  [INFERRED] [semantically similar]
  Source Code/README.md → graphify-out/converted/report_337b3c07.md
- `Reliable chunked file transfer` --semantically_similar_to--> `FILE and FILE_END`  [INFERRED] [semantically similar]
  Source Code/README.md → graphify-out/converted/report_337b3c07.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **UDP handshake security primitives** — graphify_out_converted_report_337b3c07_x25519, graphify_out_converted_report_337b3c07_hkdf, graphify_out_converted_report_337b3c07_aes_256_gcm, graphify_out_converted_report_337b3c07_ed25519, graphify_out_converted_report_337b3c07_tofu [EXTRACTED 1.00]
- **Frames carried in a DATA datagram** — graphify_out_converted_report_337b3c07_data, graphify_out_converted_report_337b3c07_stream_frame, graphify_out_converted_report_337b3c07_ack_frame, graphify_out_converted_report_337b3c07_max_stream_data, graphify_out_converted_report_337b3c07_ping, graphify_out_converted_report_337b3c07_close [EXTRACTED 1.00]
- **Network, data, and UI layers** — graphify_out_converted_report_337b3c07_three_layer_architecture, source_code_readme_common_transport_py, source_code_client_core, source_code_readme_server_server_py, source_code_readme_common_protocol_py, source_code_readme_common_crypto_py, source_code_readme_web_ui [EXTRACTED 1.00]
- **Five-layer Internet protocol stack** — graphify_out_converted_chapter_1_v9_0_177d59ed_internet_protocol_stack, graphify_out_converted_chapter_1_v9_0_177d59ed_application_layer, graphify_out_converted_chapter_1_v9_0_177d59ed_transport_layer, graphify_out_converted_chapter_1_v9_0_177d59ed_network_layer, graphify_out_converted_chapter_1_v9_0_177d59ed_link_layer, graphify_out_converted_chapter_1_v9_0_177d59ed_physical_layer [EXTRACTED 1.00]
- **Nodal delay is processing, queueing, transmission, and propagation** — graphify_out_converted_chapter_1_v9_0_177d59ed_nodal_delay, graphify_out_converted_chapter_1_v9_0_177d59ed_processing_delay, graphify_out_converted_chapter_1_v9_0_177d59ed_queueing_delay, graphify_out_converted_chapter_1_v9_0_177d59ed_transmission_delay, graphify_out_converted_chapter_1_v9_0_177d59ed_propagation_delay [EXTRACTED 1.00]
- **Internet as a network of access, regional, tier-1, IXP, and content-provider networks** — graphify_out_converted_chapter_1_v9_0_177d59ed_isp, graphify_out_converted_chapter_1_v9_0_177d59ed_access_network, graphify_out_converted_chapter_1_v9_0_177d59ed_tier1_isp, graphify_out_converted_chapter_1_v9_0_177d59ed_ixp, graphify_out_converted_chapter_1_v9_0_177d59ed_content_provider_network [EXTRACTED 1.00]
- **DNS hierarchical name resolution** — graphify_out_converted_chapter_2_v9_0_778b89a8_local_dns, graphify_out_converted_chapter_2_v9_0_778b89a8_root_dns, graphify_out_converted_chapter_2_v9_0_778b89a8_tld_dns, graphify_out_converted_chapter_2_v9_0_778b89a8_authoritative_dns [EXTRACTED 1.00]
- **E-mail compose, transfer, and retrieval** — graphify_out_converted_chapter_2_v9_0_778b89a8_user_agent, graphify_out_converted_chapter_2_v9_0_778b89a8_mail_server, graphify_out_converted_chapter_2_v9_0_778b89a8_smtp, graphify_out_converted_chapter_2_v9_0_778b89a8_imap [EXTRACTED 1.00]
- **HTTP/3 over QUIC over UDP** — graphify_out_converted_chapter_2_v9_0_778b89a8_http3, graphify_out_converted_chapter_2_v9_0_778b89a8_quic, graphify_out_converted_chapter_2_v9_0_778b89a8_udp [EXTRACTED 1.00]
- **Incremental rdt protocol family** — graphify_out_converted_chapter_3_v9_0_030c387d_rdt_1_0, graphify_out_converted_chapter_3_v9_0_030c387d_rdt_2_0, graphify_out_converted_chapter_3_v9_0_030c387d_rdt_2_1, graphify_out_converted_chapter_3_v9_0_030c387d_rdt_2_2, graphify_out_converted_chapter_3_v9_0_030c387d_rdt_3_0 [EXTRACTED 1.00]
- **TCP congestion-control phases** — graphify_out_converted_chapter_3_v9_0_030c387d_slow_start, graphify_out_converted_chapter_3_v9_0_030c387d_congestion_avoidance, graphify_out_converted_chapter_3_v9_0_030c387d_fast_recovery, graphify_out_converted_chapter_3_v9_0_030c387d_cwnd [EXTRACTED 1.00]
- **Pipelined reliable transfer** — graphify_out_converted_chapter_3_v9_0_030c387d_pipelining, graphify_out_converted_chapter_3_v9_0_030c387d_go_back_n, graphify_out_converted_chapter_3_v9_0_030c387d_selective_repeat, graphify_out_converted_chapter_3_v9_0_030c387d_tcp [EXTRACTED 1.00]
- **Router Data-Path Pipeline** — graphify_out_converted_chapter_4_v9_0_a0f1f0fc_router_architecture, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_switching_fabric, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_hol_blocking, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_buffer_management, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_packet_scheduling [EXTRACTED 1.00]
- **IPv4 Address Allocation and Translation** — graphify_out_converted_chapter_4_v9_0_a0f1f0fc_ipv4_addressing, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_cidr, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_dhcp, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_icann, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_nat [EXTRACTED 1.00]
- **Generalized Forwarding and Programmable Middleboxes** — graphify_out_converted_chapter_4_v9_0_a0f1f0fc_match_plus_action, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_openflow, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_flow_table, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_sdn, graphify_out_converted_chapter_4_v9_0_a0f1f0fc_middlebox [EXTRACTED 1.00]
- **Traditional least-cost routing algorithms** — graphify_out_converted_chapter_5_v9_0_0113e804_link_state_routing, graphify_out_converted_chapter_5_v9_0_0113e804_distance_vector_routing, graphify_out_converted_chapter_5_v9_0_0113e804_dijkstra_algorithm, graphify_out_converted_chapter_5_v9_0_0113e804_bellman_ford_equation [EXTRACTED 1.00]
- **BGP route selection criteria** — graphify_out_converted_chapter_5_v9_0_0113e804_bgp_route_selection, graphify_out_converted_chapter_5_v9_0_0113e804_local_preference, graphify_out_converted_chapter_5_v9_0_0113e804_as_path, graphify_out_converted_chapter_5_v9_0_0113e804_next_hop, graphify_out_converted_chapter_5_v9_0_0113e804_hot_potato_routing [EXTRACTED 1.00]
- **SDN controller architecture** — graphify_out_converted_chapter_5_v9_0_0113e804_sdn_controller, graphify_out_converted_chapter_5_v9_0_0113e804_northbound_api, graphify_out_converted_chapter_5_v9_0_0113e804_southbound_api, graphify_out_converted_chapter_5_v9_0_0113e804_openflow [EXTRACTED 1.00]
- **MAC Protocol Taxonomy** — graphify_out_converted_chapter_6_v9_0_4c9fd969_channel_partitioning, graphify_out_converted_chapter_6_v9_0_4c9fd969_random_access, graphify_out_converted_chapter_6_v9_0_4c9fd969_taking_turns, graphify_out_converted_chapter_6_v9_0_4c9fd969_tdma, graphify_out_converted_chapter_6_v9_0_4c9fd969_csma_cd, graphify_out_converted_chapter_6_v9_0_4c9fd969_polling [EXTRACTED 1.00]
- **Day in the Life of a Web Request** — graphify_out_converted_chapter_6_v9_0_4c9fd969_dhcp, graphify_out_converted_chapter_6_v9_0_4c9fd969_arp, graphify_out_converted_chapter_6_v9_0_4c9fd969_dns, graphify_out_converted_chapter_6_v9_0_4c9fd969_tcp, graphify_out_converted_chapter_6_v9_0_4c9fd969_http [EXTRACTED 1.00]
- **Datacenter Network Fabric** — graphify_out_converted_chapter_6_v9_0_4c9fd969_datacenter_network, graphify_out_converted_chapter_6_v9_0_4c9fd969_tor_switch, graphify_out_converted_chapter_6_v9_0_4c9fd969_leaf_spine, graphify_out_converted_chapter_6_v9_0_4c9fd969_load_balancer, graphify_out_converted_chapter_6_v9_0_4c9fd969_roce, graphify_out_converted_chapter_6_v9_0_4c9fd969_orion_sdn [EXTRACTED 1.00]
- **802.11 collision avoidance for hidden terminals** — graphify_out_converted_chapter_7_v9_0_501430a3_hidden_terminal_problem, graphify_out_converted_chapter_7_v9_0_501430a3_csma_ca, graphify_out_converted_chapter_7_v9_0_501430a3_rts_cts [EXTRACTED 1.00]
- **5G handover across RAN and core** — graphify_out_converted_chapter_7_v9_0_501430a3_handover, graphify_out_converted_chapter_7_v9_0_501430a3_gnodeb, graphify_out_converted_chapter_7_v9_0_501430a3_amf, graphify_out_converted_chapter_7_v9_0_501430a3_smf, graphify_out_converted_chapter_7_v9_0_501430a3_upf [EXTRACTED 1.00]
- **OFDMA resource-block scheduling** — graphify_out_converted_chapter_7_v9_0_501430a3_ofdma, graphify_out_converted_chapter_7_v9_0_501430a3_resource_block, graphify_out_converted_chapter_7_v9_0_501430a3_cqi, graphify_out_converted_chapter_7_v9_0_501430a3_proportional_fairness [EXTRACTED 1.00]
- **Network Security Goals** — graphify_out_converted_chapter_8_v9_0_12598a95_confidentiality, graphify_out_converted_chapter_8_v9_0_12598a95_authentication, graphify_out_converted_chapter_8_v9_0_12598a95_message_integrity, graphify_out_converted_chapter_8_v9_0_12598a95_access_and_availability [EXTRACTED 1.00]
- **IPsec Architecture** — graphify_out_converted_chapter_8_v9_0_12598a95_ipsec, graphify_out_converted_chapter_8_v9_0_12598a95_authentication_header, graphify_out_converted_chapter_8_v9_0_12598a95_esp, graphify_out_converted_chapter_8_v9_0_12598a95_security_association, graphify_out_converted_chapter_8_v9_0_12598a95_ike [EXTRACTED 1.00]
- **Operational Security Controls** — graphify_out_converted_chapter_8_v9_0_12598a95_firewall, graphify_out_converted_chapter_8_v9_0_12598a95_stateless_packet_filter, graphify_out_converted_chapter_8_v9_0_12598a95_stateful_packet_filter, graphify_out_converted_chapter_8_v9_0_12598a95_application_gateway, graphify_out_converted_chapter_8_v9_0_12598a95_intrusion_detection_system [EXTRACTED 1.00]
- **Per-user client stack** — source_code_docs_arch_browser_ui, source_code_docs_arch_http_gateway, source_code_docs_arch_client_core, source_code_docs_arch_client_transport [EXTRACTED 1.00]
- **Server processing stack** — source_code_docs_arch_session_manager, source_code_docs_arch_router, source_code_docs_arch_server_transport [EXTRACTED 1.00]
- **Encrypted multiplexed UDP session** — source_code_docs_arch_client_transport, source_code_docs_arch_udp_encrypted, source_code_docs_arch_server_transport, source_code_docs_arch_independent_udp_streams [EXTRACTED 1.00]
- **File transfer participants (A to B, cut-through relay)** — source_code_docs_seq_file_browser_a, source_code_docs_seq_file_client_a, source_code_docs_seq_file_server, source_code_docs_seq_file_client_b, source_code_docs_seq_file_browser_b [EXTRACTED 1.00]
- **Repeated cut-through chunk, relay, and credit loop** — source_code_docs_seq_file_gateway_backpressure, source_code_docs_seq_file_stream_data_chunk, source_code_docs_seq_file_relay_chunk, source_code_docs_seq_file_ack_max_stream_data, source_code_docs_seq_file_selective_retransmit [EXTRACTED 1.00]
- **File end, SHA-256 check, notify, and download** — source_code_docs_seq_file_file_end_fin, source_code_docs_seq_file_sha256_check, source_code_docs_seq_file_sse_file_progress, source_code_docs_seq_file_get_download [EXTRACTED 1.00]
- **Unicast message lifecycle from A to B** — source_code_docs_seq_msg_vong_doi_tin_nhan, source_code_docs_seq_msg_browser_a, source_code_docs_seq_msg_client_a, source_code_docs_seq_msg_server, source_code_docs_seq_msg_client_b, source_code_docs_seq_msg_browser_b [EXTRACTED 1.00]
- **Even and odd STREAM plus FIN and ACK exchange** — source_code_docs_seq_msg_client_a, source_code_docs_seq_msg_server, source_code_docs_seq_msg_client_b, source_code_docs_seq_msg_stream_sid_n, source_code_docs_seq_msg_ack_sack, source_code_docs_seq_msg_stream_sid_m, source_code_docs_seq_msg_ack, source_code_docs_seq_msg_client_a_even_stream, source_code_docs_seq_msg_server_odd_stream [EXTRACTED 1.00]
- **Send confirmation and browser SSE delivery** — source_code_docs_seq_msg_server, source_code_docs_seq_msg_client_a, source_code_docs_seq_msg_browser_a, source_code_docs_seq_msg_client_b, source_code_docs_seq_msg_browser_b, source_code_docs_seq_msg_ctrl_stream_sent, source_code_docs_seq_msg_err_user_offline, source_code_docs_seq_msg_sse_sent, source_code_docs_seq_msg_sse_msg [EXTRACTED 1.00]
- **Roster, private chat, and file transfer form one workspace** — source_code_docs_ui_screenshot_online_roster, source_code_docs_ui_screenshot_private_thread, source_code_docs_ui_screenshot_file_transfer_panel [EXTRACTED 1.00]
- **CUBIC phase, RTT, cwnd, in-flight, and loss form one transport instrument** — source_code_docs_ui_screenshot_cubic_slow_start, source_code_docs_ui_screenshot_rtt, source_code_docs_ui_screenshot_cwnd, source_code_docs_ui_screenshot_inflight, source_code_docs_ui_screenshot_loss_counter [EXTRACTED 1.00]
- **Finished big.bin send is reflected in the file card, the chat notice, and idle lossless transport counters** — source_code_docs_ui_screenshot_big_bin_transfer, source_code_docs_ui_screenshot_transfer_chat_notice, source_code_docs_ui_screenshot_inflight, source_code_docs_ui_screenshot_loss_counter [INFERRED 0.85]

## Communities (42 total, 11 thin omitted)

### Community 0 - "Chapter 1 Internet Basics"
Cohesion: 0.06
Nodes (34): Access Network, Application Layer, ARPAnet, Computer Networking: A Top-Down Approach, Chapter 1, Content Provider Network, DNS, Digital Subscriber Line (DSL), Ethernet (+26 more)

### Community 1 - "Chapter 7 Wireless Mobile"
Cohesion: 0.05
Nodes (43): 5G Core Network, 5G New Radio, Ad Hoc Network, Access and Mobility Management Function, Base Station, Bluetooth Low Energy, Bluetooth, Chapter 7 Wireless and Mobile Networks (+35 more)

### Community 2 - "Client Core Session"
Cohesion: 0.07
Nodes (10): AuthError, ClientCore, progress(), check(), MsgBuffer, Session, StreamState, Collector (+2 more)

### Community 3 - "Chapter 2 Application Layer"
Cohesion: 0.06
Nodes (37): Akamai, Application layer, Application-layer protocol, Authoritative DNS servers, BitTorrent, Computer Networking: A Top-Down Approach, 9th ed., Chapter 2 Application Layer, DASH, Domain Name System (DNS) (+29 more)

### Community 4 - "Chapter 6 Link Layer"
Cohesion: 0.06
Nodes (47): Address Resolution Protocol, Broadcast Link, Cyclic Redundancy Check, CSMA, CSMA/CA, CSMA/CD, Datacenter Network, DHCP (+39 more)

### Community 5 - "Chapter 3 Transport TCP"
Cohesion: 0.06
Nodes (52): AIMD (Additive Increase, Multiplicative Decrease), Bandwidth-Delay Product, BBR (Bottleneck Bandwidth and RTT), Bottleneck Link, TCP Congestion Avoidance, Congestion Control, Connectionless Demultiplexing, TCP Congestion Window (cwnd) (+44 more)

### Community 6 - "Crypto Packet Cipher"
Cohesion: 0.07
Nodes (11): derive_keys(), load_or_create_identity(), new_ephemeral(), PacketCipher, public_bytes(), sign(), transcript(), verify() (+3 more)

### Community 7 - "Chapter 4 Data Plane"
Cohesion: 0.06
Nodes (37): ATM CBR and ABR, Chapter 4 Network Layer Data Plane, CIDR, DHCP, Diffserv, FCFS Scheduling, Firewall, Flow Table (+29 more)

### Community 8 - "Chapter 5 Routing Control"
Cohesion: 0.06
Nodes (47): AS-PATH, Autonomous System, Bellman-Ford Equation, BGP, BGP Messages, BGP Route Selection, Count-to-Infinity Problem, Dijkstra's Algorithm (+39 more)

### Community 9 - "Chapter 8 Network Security"
Cohesion: 0.08
Nodes (43): AES, Application Gateway, Authentication Header, Certification Authority, Chapter 8 Network Security, Cryptographic Hash Function, Denial of Service, DES (+35 more)

### Community 11 - "CUBIC and BBR"
Cohesion: 0.10
Nodes (4): Bbr, CongestionControl, Cubic, make_cc()

### Community 12 - "CollabNet UI Screenshot"
Cohesion: 0.11
Nodes (23): CollabNet client workspace screenshot, Alice online session, CollabNet header bar, big.bin transfer complete (3.8 MB to bob), Mọi người broadcast channel, Message composer with attachment, CUBIC slow-start chip, Congestion window 4055 KB chip (+15 more)

### Community 13 - "Packet Wire Format"
Cohesion: 0.22
Nodes (6): decode_frames(), enc_ack(), enc_close(), enc_max_stream_data(), enc_ping(), enc_stream()

### Community 14 - "Report Figure Generation"
Cohesion: 0.12
Nodes (6): architecture(), arrow(), box(), build(), make_diagrams(), sequence()

### Community 15 - "Browser App Script"
Cohesion: 0.23
Nodes (18): addMessage(), appendLog(), connectEvents(), el(), fmtSize(), fmtTime(), H, onLogin() (+10 more)

### Community 16 - "Server Relay Routing"
Cohesion: 0.23
Nodes (4): pack(), ProtocolError, Relay, Server

### Community 17 - "Process Entry Points"
Cohesion: 0.20
Nodes (5): amain(), main(), amain(), main(), chunked()

### Community 18 - "Protocol and Benchmark"
Cohesion: 0.20
Nodes (3): safe_filename(), main(), run()

### Community 19 - "File Transfer Sequence"
Cohesion: 0.24
Nodes (14): ACK + MAX_STREAM_DATA (cấp thêm credit), Browser A, Browser B, Client A, Client B, {t:FILE_END,sha256} + FIN, GET /api/download/<tên>, relay chunk ngay khi tới (không lưu file) (+6 more)

### Community 20 - "Password and Identity"
Cohesion: 0.16
Nodes (4): fingerprint(), hash_password(), verify_password(), UserStore

### Community 21 - "Handshake and Keys"
Cohesion: 0.19
Nodes (13): AES-256-GCM, Connection state machine, Ed25519, HANDSHAKE packet 0x02, HKDF, INITIAL packet 0x01, TOFU fingerprint pin, X25519 (+5 more)

### Community 22 - "Assignment Requirements"
Cohesion: 0.22
Nodes (15): User authentication and discovery, Concurrency requirement, Connection resilience requirement, Custom application-layer protocol, HTTP UI with client-side JavaScript, Payload encryption requirement, Assignment project brief, Reliable file transfer requirement (+7 more)

### Community 24 - "Message Sequence Diagram"
Cohesion: 0.22
Nodes (14): ACK, ACK (SACK ranges), Browser A, Browser B, Client A, Client B, ctrl stream 1: {t:SENT,ref} (hoặc ERR:user offline), ERR:user offline (+6 more)

### Community 25 - "Web UI and Messages"
Cohesion: 0.21
Nodes (12): Length-prefixed JSON messages, FILE and FILE_END, MSG message, Beacon and PEERS presence, STREAM frame, Course textbook chapters 2, 3, 6, and 8, Chat composer, CollabNet web page (+4 more)

### Community 26 - "Architecture Requirements"
Cohesion: 0.22
Nodes (11): Layered architecture requirement, Three-layer architecture, client/gateway.py, common/protocol.py, common/transport.py, Connection resilience, Reliable chunked file transfer, Assignment step traceability table (+3 more)

### Community 28 - "Architecture Diagram"
Cohesion: 0.29
Nodes (11): Trình duyệt UI (HTML + JavaScript) — chat / file / peers, Client (mỗi người dùng), Client Core — AUTH · MSG · FILE, auto-reconnect, TOFU, Transport (UDP socket thô) — stream · ACK/SACK · cwnd, CUBIC/BBR · AES-GCM, HTTP Gateway (asyncio TCP, tự viết) — REST + SSE + upload, HTTP/SSE, Router — broadcast / unicast MSG, cut-through FILE relay (back-pressure), Server (+3 more)

### Community 30 - "Gateway HTTP Tests"
Cohesion: 0.24
Nodes (3): GatewayTests, http(), jpost()

### Community 32 - "Login and Discovery UI"
Cohesion: 0.22
Nodes (9): AUTH message, PBKDF2-SHA256, Tim trong LAN button, Login form, client.main entry point, client_state directory, known_hosts.json, LAN UDP beacon discovery (+1 more)

### Community 34 - "QUIC-Style Reliability"
Cohesion: 0.32
Nodes (5): BBR and CUBIC requirement, Steam GameNetworkingSockets, Google QUIC, Selective retransmission, ACK SACK frame

### Community 35 - "Flow Control Frames"
Cohesion: 0.29
Nodes (5): Sliding window sequencing, CLOSE frame, DATA packet 0x10, MAX_STREAM_DATA frame, PING frame

### Community 36 - "Loss Benchmark Tests"
Cohesion: 0.43
Nodes (7): Automated and browser test matrix, BBR, CUBIC versus BBR benchmark, CUBIC, Loss and delay simulation, server.server entry point, Unittest suite

## Ambiguous Edges - Review These
- `Custom UDP Transport` → `TCP reliable path and UDP discovery`  [AMBIGUOUS]
  graphify-out/converted/Assignment 1 - Distributed Streaming-based Client-Server Collaboration Application_1fd07668.md · relation: conceptually_related_to
- `Reliable file transfer requirement` → `TCP reliable path and UDP discovery`  [AMBIGUOUS]
  graphify-out/converted/Assignment 1 - Distributed Streaming-based Client-Server Collaboration Application_1fd07668.md · relation: conceptually_related_to
- `TCP client-server handshake step` → `INITIAL packet 0x01`  [AMBIGUOUS]
  graphify-out/converted/Assignment 1 - Distributed Streaming-based Client-Server Collaboration Application_1fd07668.md · relation: conceptually_related_to
- `4G LTE` → `Starlink`  [AMBIGUOUS]
  graphify-out/converted/Chapter_7_v9.0_501430a3.md · relation: conceptually_related_to
- `Alice online session` → `Online roster (ĐANG ONLINE 2)`  [AMBIGUOUS]
  Source Code/docs/ui_screenshot.png · relation: conceptually_related_to
- `Mọi người broadcast channel` → `Outgoing greeting bubble`  [AMBIGUOUS]
  Source Code/docs/ui_screenshot.png · relation: conceptually_related_to

## Knowledge Gaps
- **83 isolated node(s):** `docs/build_report.py`, `style.css`, `Internet Engineering Task Force (IETF)`, `Software-Defined Networking (SDN)`, `BitTorrent` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 226 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Connection` connect `Connection Send Path` to `Receive Stream Reassembly`, `Rate Sample`, `Crypto Packet Cipher`, `CUBIC and BBR`, `Packet Wire Format`, `Range Set Tests`, `Send Stream Window`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Connection` (e.g. with `RateSample` and `RangeSet`) actually correct?**
  _`Connection` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `docs/build_report.py`, `style.css`, `Internet Engineering Task Force (IETF)` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Chapter 1 Internet Basics` be split into smaller, more focused modules?**
  _Cohesion score 0.05952380952380952 - nodes in this community are weakly interconnected._
- **Why does `Endpoint` connect `Crypto Packet Cipher` to `Client Core Session`, `Packet Wire Format`, `Server Relay Routing`, `Process Entry Points`, `Protocol and Benchmark`, `Password and Identity`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Custom UDP Transport` and `TCP reliable path and UDP discovery`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Reliable file transfer requirement` and `TCP reliable path and UDP discovery`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._