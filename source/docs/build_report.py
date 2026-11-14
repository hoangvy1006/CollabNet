"""Generates docs/report.pdf (architecture, protocol spec, sequence diagrams, challenges). Run from project root:
    python docs/build_report.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, Preformatted)

HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", FD + "DejaVuSansMono.ttf"))
plt.rcParams["font.family"] = "DejaVu Sans"


# ------------------------------------------------------------------ diagrams
def box(ax, x, y, w, h, text, fc="#e8f0fe", ec="#2f6fed", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, x1, y1, x2, y2, text="", both=True, color="#444"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="<->" if both else "->", color=color, lw=1.4))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text, ha="center", fontsize=8, color=color)


def architecture():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")
    ax.text(0.2, 5.3, "Client (mỗi người dùng)", fontsize=10, weight="bold")
    box(ax, 0.2, 3.9, 2.1, 1.0, "Trình duyệt\nUI (HTML + JavaScript)\nchat / file / peers")
    box(ax, 3.1, 3.9, 2.4, 1.0, "HTTP Gateway\n(asyncio TCP, tự viết)\nREST + SSE + upload", fc="#fff4e0", ec="#e0a100")
    box(ax, 3.1, 2.3, 2.4, 1.1, "Client Core\nAUTH · MSG · FILE\nauto-reconnect, TOFU", fc="#e6f6ea", ec="#1f9d55")
    box(ax, 3.1, 0.7, 2.4, 1.2, "Transport (UDP socket thô)\nstream · ACK/SACK · cwnd\nCUBIC/BBR · AES-GCM", fc="#f3e8ff", ec="#8a4fff")
    arrow(ax, 2.3, 4.4, 3.1, 4.4, "HTTP/SSE")
    arrow(ax, 4.3, 3.9, 4.3, 3.4)
    arrow(ax, 4.3, 2.3, 4.3, 1.9)
    ax.text(6.2, 5.3, "Server", fontsize=10, weight="bold")
    box(ax, 6.6, 3.9, 3.0, 1.0, "Session manager\nAUTH (PBKDF2) · presence\nip:port của từng user", fc="#e6f6ea", ec="#1f9d55")
    box(ax, 6.6, 2.3, 3.0, 1.1, "Router\nbroadcast / unicast MSG\ncut-through FILE relay\n(back-pressure)", fc="#e6f6ea", ec="#1f9d55")
    box(ax, 6.6, 0.7, 3.0, 1.2, "Transport (giống client)\nđịnh danh Ed25519\nBeacon broadcast (discovery)", fc="#f3e8ff", ec="#8a4fff")
    arrow(ax, 8.1, 3.9, 8.1, 3.4)
    arrow(ax, 8.1, 2.3, 8.1, 1.9)
    arrow(ax, 5.5, 1.3, 6.6, 1.3, "UDP\n(mã hoá)", color="#8a4fff")
    ax.text(5.5, 0.15, "Nhiều stream độc lập trong 1 kết nối UDP: ctrl · mỗi tin nhắn 1 stream · mỗi file 1 stream",
            ha="center", fontsize=8.5, style="italic")
    ax.plot([5.8, 5.8], [2.0, 5.2], ls=":", c="#bbb")
    fig.savefig(os.path.join(HERE, "arch.png"), dpi=170, bbox_inches="tight"); plt.close(fig)


def sequence(fname, title, actors, steps, height):
    fig, ax = plt.subplots(figsize=(10, height))
    n = len(actors)
    xs = [1.2 + i * (7.6 / (n - 1)) for i in range(n)]
    top, bottom = height - 0.6, 0.2
    ax.set_xlim(0, 10); ax.set_ylim(0, height); ax.axis("off")
    ax.text(5, height - 0.15, title, ha="center", fontsize=11, weight="bold")
    for x, a in zip(xs, actors):
        box(ax, x - 0.75, top - 0.35, 1.5, 0.45, a, fs=9)
        ax.plot([x, x], [bottom, top - 0.35], ls="--", c="#999", lw=1)
    y = top - 0.8
    for s in steps:
        if s[0] == "note":
            ax.text(5, y, s[1], ha="center", fontsize=8, style="italic", color="#555",
                    bbox=dict(fc="#fffbe6", ec="#e0c200", boxstyle="round,pad=0.25"))
            y -= 0.5
            continue
        a, b, txt = s
        x1, x2 = xs[a], xs[b]
        ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color="#2f6fed", lw=1.3))
        ax.text((x1 + x2) / 2, y + 0.08, txt, ha="center", va="bottom", fontsize=7.8)
        y -= 0.48
    fig.savefig(os.path.join(HERE, fname), dpi=170, bbox_inches="tight"); plt.close(fig)


def make_diagrams():
    architecture()
    sequence("seq_msg.png", "Vòng đời một tin nhắn (A gửi unicast cho B)", ["Browser A", "Client A", "Server", "Client B", "Browser B"], [
        (0, 1, "POST /api/send {to:B,text}"),
        ("note", "Client A mở stream MỚI (id chẵn), 1 gói UDP mã hoá AES-GCM"),
        (1, 2, "STREAM(sid=n) {t:MSG,id,to,text} + FIN"),
        (2, 1, "ACK (SACK ranges)"),
        ("note", "Server kiểm tra, gắn from/ts, mở stream MỚI (id lẻ) tới B"),
        (2, 3, "STREAM(sid=m) {t:MSG,from:A,...} + FIN"),
        (3, 2, "ACK"),
        (2, 1, "ctrl stream 1: {t:SENT,ref}   (hoặc ERR: user offline)"),
        (3, 4, "SSE event: msg"),
        (1, 0, "SSE event: sent  (✓ đã gửi)"),
    ], 6.3)
    sequence("seq_file.png", "Vòng đời một lần truyền file (A → B, cut-through relay)", ["Browser A", "Client A", "Server", "Client B", "Browser B"], [
        (0, 1, "XHR POST /api/upload  (body = File, X-To, X-Filename)"),
        (1, 2, "STREAM(prio 1): {t:FILE,to,name,size}"),
        (2, 3, "STREAM mới: {t:FILE,from,name,size}  (header do server tạo lại)"),
        ("note", "Lặp lại: gateway đọc 64 KB → send → await drain() (back-pressure vào TCP của trình duyệt)"),
        (1, 2, "STREAM data chunk (offset tăng dần, sliding window)"),
        (2, 3, "relay chunk ngay khi tới (không lưu file)"),
        (3, 2, "ACK + MAX_STREAM_DATA (cấp thêm credit)"),
        ("note", "Mất gói → chỉ retransmit đoạn byte thiếu; stream chat khác không bị chặn"),
        (1, 2, "{t:FILE_END,sha256} + FIN"),
        (3, 4, "SSE: file_progress ... file_received (đã kiểm tra SHA-256)"),
        (4, 3, "GET /api/download/<tên>"),
    ], 6.9)


# ------------------------------------------------------------------ PDF
def build():
    make_diagrams()
    ss = getSampleStyleSheet()
    base = ParagraphStyle("b", parent=ss["Normal"], fontName="DV", fontSize=9.6, leading=14)
    h1 = ParagraphStyle("h1", parent=base, fontName="DV-B", fontSize=14, leading=18, spaceBefore=10, spaceAfter=6,
                        textColor=colors.HexColor("#1b3a8a"))
    h2 = ParagraphStyle("h2", parent=base, fontName="DV-B", fontSize=11, leading=15, spaceBefore=8, spaceAfter=3)
    title = ParagraphStyle("t", parent=base, fontName="DV-B", fontSize=20, leading=26, alignment=TA_CENTER)
    sub = ParagraphStyle("s", parent=base, alignment=TA_CENTER, textColor=colors.grey)
    cell = ParagraphStyle("c", parent=base, fontSize=8.4, leading=11)
    cellb = ParagraphStyle("cb", parent=cell, fontName="DV-B")
    code = ParagraphStyle("code", parent=base, fontName="DVM", fontSize=7.6, leading=10,
                          backColor=colors.HexColor("#f4f5f7"), borderPadding=5)
    P = lambda t, s=base: Paragraph(t, s)

    def table(rows, widths, header=True):
        data = [[P(str(c), cellb if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
        t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
        st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9ced8")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
        if header:
            st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f0fe")))
        t.setStyle(TableStyle(st))
        return t

    def img(name, w=17):
        from PIL import Image as PI
        iw, ih = PI.open(os.path.join(HERE, name)).size
        return Image(os.path.join(HERE, name), width=w * cm, height=w * cm * ih / iw)

    S = []
    S += [Spacer(1, 3 * cm), P("BÁO CÁO KỸ THUẬT", sub), Spacer(1, 6),
          P("Distributed Streaming-based<br/>Client-Server Collaboration Application", title), Spacer(1, 10),
          P("Môn: Network Application Development · Assignment 1", sub), Spacer(1, 1.2 * cm),
          P("Hệ thống chat, phát hiện người dùng và truyền file thời gian thực chạy trên <b>UDP thuần</b>, "
            "với transport tin cậy tự xây dựng (đa stream, sliding window, ACK/SACK, retransmit chọn lọc, CUBIC/BBR) "
            "và mã hoá AES-256-GCM. Giao diện web bằng HTTP + JavaScript phía client.", base),
          Spacer(1, 0.8 * cm)]
    S.append(table([["Hạng mục", "Nội dung"],
                    ["Ngôn ngữ / thư viện", "Python 3.10+; chỉ dùng <b>socket</b> thô + asyncio; 1 thư viện ngoài: <i>cryptography</i> (AES-GCM, X25519, Ed25519, HKDF)"],
                    ["Không dùng", "Flask/Django, WebSocket, QUIC/aioquic, thư viện mạng cấp cao"],
                    ["Giao thức", "Giao thức tầng ứng dụng + transport tự thiết kế (xem mục 2)"],
                    ["Kiểm thử", "19 test tự động (unit, transport, e2e, gateway) + kiểm thử trình duyệt thật bằng Chromium"]],
                   [4.2 * cm, 12.8 * cm]))
    S.append(PageBreak())

    # 1. Architecture
    S += [P("1. Kiến trúc hệ thống", h1),
          P("Hệ thống tách bạch ba lớp: <b>logic mạng</b> (common/transport.py, client/core.py, server/server.py), "
            "<b>xử lý dữ liệu</b> (protocol.py, crypto.py) và <b>giao diện</b> (client/web: HTML + JS thuần). "
            "Trình duyệt chỉ nói chuyện HTTP với gateway cục bộ; mọi giao tiếp giữa các máy đều là UDP.", base),
          Spacer(1, 6), img("arch.png", 16.5),
          P("Quyết định thiết kế chính", h2)]
    S.append(table([["Vấn đề", "Giải pháp", "Liên hệ lý thuyết (giáo trình)"],
                    ["Tin cậy trên UDP", "Số hiệu gói tăng đơn điệu (mỗi lần gửi lại dùng số mới), ACK dạng dải (SACK), "
                     "phát hiện mất gói bằng ngưỡng 3 gói + ngưỡng thời gian 9/8 RTT + PTO", "Ch.3: rdt, Go-Back-N / Selective Repeat, TCP RTT"],
                    ["Không bị Head-of-Line blocking", "Mỗi tin nhắn / mỗi file là một <b>stream</b> riêng; chỉ byte trong cùng stream mới phải đúng thứ tự", "Ch.2: HTTP/2→HTTP/3, QUIC"],
                    ["Điều khiển luồng", "Cửa sổ nhận trượt theo từng stream (MAX_STREAM_DATA), 512 KB; server giữ credit khi người nhận chậm (back-pressure)", "Ch.3: flow control, rwnd"],
                    ["Điều khiển tắc nghẽn", "CUBIC (mặc định) hoặc BBR (<code>--cc bbr</code>) + pacing", "Ch.3: AIMD, CUBIC, BBR"],
                    ["Bảo mật", "X25519 tạm thời (forward secrecy) → HKDF → 2 khoá AES-256-GCM; server ký handshake bằng Ed25519, client ghim "
                     "fingerprint (TOFU); header là AAD; cửa sổ chống replay", "Ch.8: DH, chữ ký số, MITM, TLS 1.3, IPsec replay window"],
                    ["Phát hiện / presence", "Server broadcast beacon UDP; danh sách peers (user, ip, port) do server duy trì và đẩy mỗi khi thay đổi", "Ch.2, Ch.6"]],
                   [3.3 * cm, 8.4 * cm, 5.3 * cm]))
    S.append(PageBreak())

    # 2. Protocol
    S += [P("2. Đặc tả giao thức", h1), P("2.1 Datagram (tầng transport)", h2),
          Preformatted("+------+-----------+------------------+-------------------------------+---------+\n"
                       "| type | dest_cid  |   packet number  |  frames, mã hoá AES-256-GCM   | GCM tag |\n"
                       "| 1 B  |   4 B     |       8 B        |          (<= 1171 B)          |  16 B   |\n"
                       "+------+-----------+------------------+-------------------------------+---------+\n"
                       " \\_____ header 13 B (được xác thực làm AAD) ____/    MTU datagram = 1200 B", code),
          Spacer(1, 4)]
    S.append(table([["type", "Ý nghĩa", "Nội dung"],
                    ["0x01 INITIAL", "Client hello (rõ)", "client_cid(4) + X25519 public(32); client gửi lại với backoff 0.25→1 s"],
                    ["0x02 HANDSHAKE", "Server hello (rõ)", "server_cid(4) + X25519 public(32) + Ed25519 public(32) + chữ ký(64) trên transcript"],
                    ["0x10 DATA", "Gói ứng dụng", "pn(8) tăng đơn điệu; nonce = 0⁴ ‖ pn; khoá riêng cho mỗi chiều"]],
                   [3.2 * cm, 3.3 * cm, 10.5 * cm]))
    S += [P("2.2 Frame (bên trong gói DATA đã giải mã)", h2)]
    S.append(table([["Frame", "Trường", "Mục đích"],
                    ["STREAM 0x02 / 0x03(FIN)", "stream_id(4) offset(8) length(2) data", "Dữ liệu theo byte-offset; FIN đánh dấu hết stream"],
                    ["ACK 0x04", "largest(8) delay_us(4) n(1) n×[start(8) end(8)]", "SACK: tối đa 6 dải gói đã nhận → chỉ gửi lại đoạn thiếu"],
                    ["MAX_STREAM_DATA 0x05", "stream_id(4) max_offset(8)", "Cấp thêm credit (cửa sổ trượt) cho người gửi"],
                    ["PING 0x06", "—", "Keep-alive / heartbeat mỗi 4 s khi rảnh; probe khi PTO"],
                    ["CLOSE 0x07", "code(2) len(2) reason", "Đóng kết nối có lý do (gửi 3 lần)"]],
                   [4.2 * cm, 6.2 * cm, 6.6 * cm]))
    S += [P("2.3 Thông điệp ứng dụng (u32 độ dài + JSON UTF-8, luôn có trường <b>t</b>)", h2)]
    S.append(table([["Stream", "Thông điệp", "Hướng", "Mô tả"],
                    ["client #0 (ctrl)", "AUTH {user,pass}", "C→S", "Đăng nhập; tên mới được tự đăng ký (PBKDF2-SHA256 120k vòng + salt)"],
                    ["client #0", "LIST / BYE", "C→S", "Yêu cầu danh sách peers / thoát"],
                    ["server #1 (ctrl)", "AUTH_OK {user,peers} · AUTH_FAIL {msg}", "S→C", "Kết quả đăng nhập"],
                    ["server #1", "PEERS {peers:[{user,ip,port,since}]}", "S→C", "Cập nhật presence (khi ai đó vào/ra)"],
                    ["server #1", "SENT {ref,n} · ERR {ref,msg}", "S→C", "Xác nhận đã chuyển / lỗi (user offline, file quá lớn…)"],
                    ["mỗi tin nhắn", "MSG {id,to,text}  (to = tên hoặc *)", "C→S→C", "Một stream mới + FIN; server thêm from, ts rồi chuyển tiếp"],
                    ["mỗi file", "FILE {id,to,name,size} · bytes · FILE_END {sha256}", "C→S→C", "Một stream mới (ưu tiên thấp); server dựng lại header tin cậy và relay cut-through"]],
                   [2.8 * cm, 5.6 * cm, 1.6 * cm, 7.0 * cm]))
    S += [P("2.4 Máy trạng thái kết nối", h2),
          Preformatted("  CLIENT                                             SERVER\n"
                       "  CONNECTING --INITIAL(cid,epk)--------------------> (tạo Connection, cache reply)\n"
                       "             <-HANDSHAKE(cid',epk',pk,sig)--------- \n"
                       "  (verify sig + pin) --> ESTABLISHED <-- keys (HKDF) --> ESTABLISHED\n"
                       "  AUTH (stream 0, mã hoá) ----------------------------> kiểm tra mật khẩu\n"
                       "             <-AUTH_OK / AUTH_FAIL (stream 1)-------- ONLINE  --> PEERS tới mọi người\n"
                       "  idle > 20 s hoặc CLOSE ---------------------------> OFFLINE --> PEERS cập nhật\n"
                       "  mất kết nối bất ngờ -> RECONNECTING (backoff 1,2,4..15 s) -> đăng nhập lại tự động", code)]
    S.append(PageBreak())

    # 3. Sequence diagrams
    S += [P("3. Sơ đồ tuần tự", h1), img("seq_msg.png", 16.5), Spacer(1, 8), img("seq_file.png", 16.5), PageBreak()]

    # 4. UI / tests / benchmark
    S += [P("4. Giao diện và kết quả kiểm thử", h1),
          P("Giao diện web (HTTP + JavaScript phía client) hiển thị tin nhắn, danh sách người dùng đang online (kèm IP:port), "
            "thanh tiến trình truyền file (gửi/nhận) và chỉ số mạng thời gian thực (thuật toán CC, RTT, cwnd, gói mất).", base),
          Spacer(1, 4), img("ui_screenshot.png", 16.5), Spacer(1, 6)]
    S.append(table([["Nhóm test", "Nội dung kiểm tra", "KQ"],
                    ["Unit", "RangeSet, mã hoá/giải mã frame, crypto (ECDH, AES-GCM chống sửa header, PBKDF2)", "OK"],
                    ["Transport", "4 MB sạch; 5% mất gói + reorder (CUBIC, BBR) – SHA-256 khớp; flow control chặn đúng cửa sổ; "
                     "từ chối server sai khoá; phát hiện ngắt kết nối", "OK"],
                    ["No-HoL", "Tin chat nhỏ trong khi file 3 MB đang truyền, 3% mất gói: độ trễ ~21 ms/tin", "OK"],
                    ["E2E (3 client)", "Đăng nhập, presence, broadcast, unicast không rò rỉ, user offline→ERR, file 3 MB + file rỗng, client biến mất đột ngột, "
                     "đăng nhập trùng, auto-reconnect — chạy cả trên link 4% mất gói + 15 ms (BBR)", "OK"],
                    ["Gateway HTTP", "Tĩnh/API/SSE, upload stream qua POST, tải về, chặn thiếu X-Requested-With, chặn Host lạ, chặn path traversal", "OK"],
                    ["Trình duyệt thật", "Chromium điều khiển 2 người dùng: chat, tin riêng, gửi file 4 MB, tải về đúng SHA-256, 0 lỗi JS", "OK"]],
                   [2.8 * cm, 12.6 * cm, 1.6 * cm]))
    bench = json.load(open(os.path.join(HERE, "benchmark.json")))
    rows = [["Mất gói", "CUBIC (Mbps)", "BBR (Mbps)"]]
    for loss in sorted({r["loss"] for r in bench}):
        c = next(r for r in bench if r["loss"] == loss and r["cc"] == "cubic")
        b = next(r for r in bench if r["loss"] == loss and r["cc"] == "bbr")
        rows.append([f"{loss * 100:.0f}%", c["mbps"], b["mbps"]])
    S += [P("Hiệu năng: CUBIC so với BBR (2 MB, RTT 20 ms mô phỏng)", h2), table(rows, [4 * cm, 4 * cm, 4 * cm]), Spacer(1, 4),
          P("Khi không mất gói, CUBIC nhỉnh hơn nhẹ (slow-start tích cực). Khi mất gói 1–5%, CUBIC giảm cửa sổ ×0.7 ở mỗi lần mất nên "
            "thông lượng sụp, còn BBR dựa trên mô hình băng thông/RTT nên gần như không bị ảnh hưởng — đúng với phân tích ở Ch.3 "
            "(loss-based vs model-based). Đây là lý do cho phép chọn thuật toán bằng tham số.", base), PageBreak()]

    # 5. Challenges (1 page)
    S += [P("5. Thách thức gặp phải và cách giải quyết", h1)]
    ch = [
        ("Head-of-line blocking khi chat cùng file lớn",
         "Nếu mọi thứ nằm trong một byte-stream (như TCP) thì một gói file mất sẽ chặn cả tin nhắn. Giải pháp: transport đa stream; mỗi tin nhắn/file một stream, "
         "lập lịch ưu tiên (chat ưu tiên cao hơn file) và round-robin giữa các file. Đo được độ trễ chat ≈ 21 ms dù file đang truyền với 3% mất gói."),
        ("Mơ hồ khi đo RTT / phân biệt gửi lại",
         "Giống TCP, ACK của gói gửi lại gây nhập nhằng. Dùng số hiệu gói mới cho mọi lần gửi (kiểu QUIC) và ghi nhớ frame nào nằm trong gói nào; "
         "khi gói bị coi là mất chỉ đưa lại <i>dải byte</i> tương ứng vào hàng đợi retransmit — không gửi lại cả file."),
        ("Phân mảnh (fragmentation) gói UDP",
         "Datagram luôn ≤ 1200 B (dưới MTU) và tự phân đoạn dữ liệu thành frame STREAM, tránh phân mảnh IP — thứ làm mất cả gói khi một mảnh mất."),
        ("Deadlock do back-pressure khi relay file",
         "Server giữ credit của người gửi khi hàng đợi gửi tới người nhận quá lớn. Lỗi thật gặp: lần giữ credit thứ hai <b>ghi đè</b> callback của lần trước nên "
         "credit không bao giờ được trả và luồng gửi đứng vĩnh viễn khi link mất gói. Sửa bằng danh sách callback + giải phóng toàn bộ khi người nhận đóng kết nối "
         "(phát hiện nhờ test e2e có mất gói)."),
        ("Mất kết nối bất ngờ / NAT",
         "Keep-alive PING 4 s, idle timeout 20 s ở cả hai phía; server gỡ user và phát PEERS mới; client tự kết nối lại với backoff lũy tiến và đăng nhập lại; "
         "gói hợp lệ từ địa chỉ mới sẽ cập nhật địa chỉ peer (connection migration); đăng nhập trùng sẽ đá phiên cũ."),
        ("Bảo mật trên UDP",
         "Không có TLS sẵn: tự ghép các primitive chuẩn (X25519+HKDF+AES-GCM), ký handshake bằng Ed25519 để chống MITM (slide 8-41), ghim khoá kiểu SSH, "
         "nonce không bao giờ lặp nhờ số hiệu gói đơn điệu, cửa sổ chống replay, giới hạn số stream/credit để tránh cạn bộ nhớ."),
        ("Trình duyệt không nói UDP, và cấm framework",
         "Viết HTTP server tối giản trên asyncio TCP (parser + SSE + upload stream). Upload dùng XHR với Content-Length, gateway đọc từng 64 KB và "
         "<i>await drain()</i> nên áp lực ngược truyền tới TCP của trình duyệt; chặn CSRF/DNS-rebinding bằng header riêng + kiểm tra Host."),
    ]
    S.append(table([["Thách thức", "Giải pháp"]] + [[a, b] for a, b in ch], [4.0 * cm, 13.0 * cm]))
    S += [Spacer(1, 6), P("<b>Hạn chế đã biết:</b> chưa có chống khuếch đại/giả mạo địa chỉ ở INITIAL (cần cookie/retry như QUIC), "
                          "BBR là bản rút gọn v1, danh sách stream đã kết thúc (chống replay) lưu trong RAM, "
                          "chỉ hỗ trợ IPv4.", base)]

    doc = SimpleDocTemplate(os.path.join(HERE, "report.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="CollabNet - Technical Report")
    def footer(c, d):
        c.setFont("DV", 8); c.setFillColor(colors.grey)
        c.drawCentredString(A4[0] / 2, 1 * cm, f"CollabNet — Technical Explanation Report — trang {d.page}")
    doc.build(S, onFirstPage=footer, onLaterPages=footer)
    print("report.pdf written")


if __name__ == "__main__":
    build()
