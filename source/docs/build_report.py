"""Sinh docs/report.pdf (kiến trúc, giao thức, sơ đồ tuần tự, kiểm thử, các module chính, thách thức).
Chạy từ thư mục gốc dự án:
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


def _first(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0]


# DejaVu (Linux) hoặc font Windows có đủ dấu tiếng Việt; cùng bộ tên DV / DV-B / DVM cho phần thân văn bản.
FD = "/usr/share/fonts/truetype/dejavu/"
WIN = "C:/Windows/Fonts/"
REG = _first([FD + "DejaVuSans.ttf", WIN + "segoeui.ttf", WIN + "arial.ttf"])
BOLD = _first([FD + "DejaVuSans-Bold.ttf", WIN + "segoeuib.ttf", WIN + "seguisb.ttf", WIN + "arialbd.ttf"])
MONO = _first(["/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf", FD + "DejaVuSansMono.ttf", WIN + "consola.ttf", WIN + "cour.ttf"])
pdfmetrics.registerFont(TTFont("DV", REG))
pdfmetrics.registerFont(TTFont("DV-B", BOLD))
pdfmetrics.registerFont(TTFont("DVM", MONO))
from matplotlib.font_manager import FontProperties                      # noqa: E402
plt.rcParams["font.family"] = FontProperties(fname=BOLD).get_name()


# ------------------------------------------------------------------ sơ đồ
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
    box(ax, 3.1, 2.3, 2.4, 1.1, "Client Core\nAUTH · MSG · P2P FILE\nauto-reconnect, TOFU", fc="#e6f6ea", ec="#1f9d55")
    box(ax, 3.1, 0.7, 2.4, 1.2, "Transport (UDP socket thô)\nstream · ACK/SACK · cwnd\nCUBIC/BBR · AES-GCM", fc="#f3e8ff", ec="#8a4fff")
    arrow(ax, 2.3, 4.4, 3.1, 4.4, "HTTP/SSE")
    arrow(ax, 4.3, 3.9, 4.3, 3.4)
    arrow(ax, 4.3, 2.3, 4.3, 1.9)
    ax.text(6.2, 5.3, "Server", fontsize=10, weight="bold")
    box(ax, 6.6, 3.9, 3.0, 1.0, "Session manager\nAUTH (PBKDF2) · presence\nip:port của từng user", fc="#e6f6ea", ec="#1f9d55")
    box(ax, 6.6, 2.3, 3.0, 1.1, "Router\nbroadcast / unicast MSG\nkhông nhận file (P2P)\nlịch sử chat (history.json)", fc="#e6f6ea", ec="#1f9d55")
    box(ax, 6.6, 0.7, 3.0, 1.2, "Transport (giống client)\nđịnh danh Ed25519\nBeacon broadcast (discovery)", fc="#f3e8ff", ec="#8a4fff")
    arrow(ax, 8.1, 3.9, 8.1, 3.4)
    arrow(ax, 8.1, 2.3, 8.1, 1.9)
    arrow(ax, 5.5, 1.3, 6.6, 1.3, "UDP\n(mã hoá)", color="#8a4fff")
    arrow(ax, 5.5, 2.85, 6.6, 2.85, "TCP\nHELLO/ACK", both=False, color="#e0a100")
    ax.text(5.5, 0.15, "Nhiều stream độc lập trong 1 kết nối UDP: ctrl · mỗi tin nhắn 1 stream · mỗi file 1 stream (P2P: client ↔ client)",
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
        (1, 0, "SSE event: sent  (đã gửi)"),
    ], 6.3)
    sequence("seq_file.png", "Vòng đời một lần truyền file (A → B, kết nối P2P trực tiếp)", ["Browser A", "Client A", "Server", "Client B", "Browser B"], [
        (0, 1, "XHR POST /api/upload  (body = File, X-To, X-Filename)"),
        (1, 2, "ctrl: LIST (xin địa chỉ + khoá P2P của B)"),
        (2, 1, "PEERS {user:B, ip, p2p_port, p2p_fp}"),
        ("note", "Server chỉ giới thiệu địa chỉ/khoá; không nhận một byte nội dung nào"),
        (1, 3, "INITIAL/HANDSHAKE trực tiếp (X25519 + Ed25519, verify fingerprint)"),
        (1, 3, "STREAM(prio 1): {t:FILE,to,name,size}"),
        (1, 3, "STREAM data 64 KB/lần: gateway đọc → send → await drain()"),
        (3, 1, "ACK + MAX_STREAM_DATA (cấp thêm credit)"),
        ("note", "Mất gói → chỉ gửi lại đoạn byte thiếu; tin chat đi đường khác nên không bị chặn"),
        (1, 3, "{t:FILE_END,sha256} + FIN"),
        (3, 4, "SSE: file_progress ... file_received (đã kiểm tra SHA-256)"),
        (4, 3, "GET /api/download/<tên>  (HTTP qua loopback)"),
    ], 7.3)


# ------------------------------------------------------------------ xuất PDF
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
    code_s = ParagraphStyle("code_s", parent=code, fontSize=7.1, leading=9.2)
    h3 = ParagraphStyle("h3", parent=base, fontName="DV-B", fontSize=9.8, leading=13, spaceBefore=7, spaceAfter=2,
                        textColor=colors.HexColor("#1b3a8a"))
    bullet = ParagraphStyle("bl", parent=base, fontSize=9.0, leading=12.2, leftIndent=11, spaceBefore=1)
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
            "và mã hoá AES-256-GCM. Trước khi dùng UDP, client <b>bắt tay TCP</b> với server (HELLO → HELLO_ACK) cùng số cổng. "
            "Giao diện web bằng HTTP + JavaScript phía client.", base),
          Spacer(1, 0.8 * cm)]
    S.append(table([["Hạng mục", "Nội dung"],
                    ["Ngôn ngữ / thư viện", "Python 3.10+; chỉ dùng <b>socket</b> thô + asyncio; 1 thư viện ngoài: <i>cryptography</i> (AES-GCM, X25519, Ed25519, HKDF)"],
                    ["Không dùng", "Flask/Django, WebSocket, QUIC/aioquic, thư viện mạng cấp cao"],
                    ["Giao thức", "Bắt tay TCP HELLO/ACK (mục 2.0) rồi tầng ứng dụng + transport tự thiết kế trên UDP (xem mục 2); file đi P2P (xem mục 2.3, 5.11)"],
                    ["Kiểm thử", "62 kiểm thử tự động (unit, transport, e2e, gateway, bắt tay TCP, hồi quy) + thử trình duyệt thật bằng Chromium"],
                    ["Nội dung báo cáo", "Kiến trúc · giao thức · sơ đồ tuần tự · giao diện và kết quả đo · các module chính kèm đoạn mã tiêu biểu · thách thức"]],
                   [4.2 * cm, 12.8 * cm]))
    S.append(PageBreak())

    # 1. Kiến trúc
    S += [P("1. Kiến trúc hệ thống", h1),
          P("Hệ thống tách bạch ba lớp: <b>logic mạng</b> (common/transport.py, client/core.py, server/server.py), "
            "<b>xử lý dữ liệu</b> (protocol.py, crypto.py) và <b>giao diện</b> (client/web: HTML + JS thuần). "
            "Trình duyệt chỉ nói chuyện HTTP với gateway cục bộ. Giữa các máy: client mở <b>kết nối TCP</b> tới server để bắt tay "
            "(HELLO → HELLO_ACK, nhận xác nhận và cổng UDP), sau đó toàn bộ dữ liệu (đăng nhập, chat, presence, file P2P) đi trên <b>UDP</b> mã hoá. "
            "Server còn giữ tài khoản (server/users.py) và lịch sử chat (server/history.py); file đi trực tiếp "
            "giữa hai client (P2P). Mục 5 trích đoạn mã quyết định của từng file.", base),
          Spacer(1, 6), img("arch.png", 12),
          P("Quyết định thiết kế chính", h2)]
    S.append(table([["Vấn đề", "Giải pháp", "Liên hệ lý thuyết (giáo trình)"],
                    ["Kết nối + xác nhận (bước 2 của đề)", "Client kết nối TCP tới server (cùng cổng với UDP), gửi HELLO; server trả HELLO_ACK {udp_port, fp} rồi đóng TCP (mục 2.0)", "Ch.3: TCP 3-way handshake, socket API"],
                    ["Tin cậy trên UDP", "Số hiệu gói tăng đơn điệu (mỗi lần gửi lại dùng số mới), ACK dạng dải (SACK), "
                     "phát hiện mất gói bằng ngưỡng 3 gói + ngưỡng thời gian 9/8 RTT + PTO", "Ch.3: rdt, Go-Back-N / Selective Repeat, TCP RTT"],
                    ["Không bị Head-of-Line blocking", "Mỗi tin nhắn / mỗi file là một <b>stream</b> riêng; chỉ byte trong cùng stream mới phải đúng thứ tự", "Ch.2: HTTP/2→HTTP/3, QUIC"],
                    ["Điều khiển luồng", "Cửa sổ nhận trượt theo từng stream (MAX_STREAM_DATA), 512 KB; bên gửi chờ drain() khi đệm đầy (back-pressure)", "Ch.3: flow control, rwnd"],
                    ["Điều khiển tắc nghẽn", "CUBIC (mặc định) hoặc BBR (<i>--cc bbr</i>) + pacing", "Ch.3: AIMD, CUBIC, BBR"],
                    ["Bảo mật", "X25519 tạm thời (forward secrecy) → HKDF → 2 khoá AES-256-GCM; server ký handshake bằng Ed25519, client ghim "
                     "fingerprint (TOFU); header là AAD; cửa sổ chống replay", "Ch.8: DH, chữ ký số, MITM, TLS 1.3, IPsec replay window"],
                    ["Phát hiện / presence", "Server broadcast beacon UDP; danh sách peers (user, ip, port) do server duy trì và đẩy mỗi khi thay đổi", "Ch.2, Ch.6"],
                    ["Truyền file", "Hai client bắt tay TRỰC TIẾP bằng chính transport này; server chỉ công bố ip/port + fingerprint Ed25519 của peer trong PEERS", "Ch.2, Ch.8: mô hình ngang hàng, xác thực khoá công khai"],
                    ["Lịch sử chat", "Server ghi mỗi tin đã định tuyến vào history.json (debounce 1 s, ghi nguyên tử) và gửi lại qua HISTORY ngay sau AUTH_OK", "Ch.2: trạng thái phiên, lưu trữ phía server"]],
                   [3.3 * cm, 8.4 * cm, 5.3 * cm]))

    S.append(PageBreak())

    # 2. Giao thức
    S += [P("2. Đặc tả giao thức", h1), P("2.0 Bắt tay TCP (kết nối + xác nhận)", h2),
          P("Server mở socket TCP và UDP <b>cùng số cổng</b> (mặc định 9000). Khi đăng nhập, client làm bước này trước tiên; "
            "nếu không kết nối được TCP, client báo lỗi rõ ràng <i>cannot reach server over TCP</i> và không thử UDP.", base),
          Spacer(1, 3)]
    S.append(table([["Bước", "Gói tin", "Nội dung"],
                    ["1", "TCP SYN → SYN/ACK → ACK", "Bắt tay 3 bước của hệ điều hành (socket.connect)"],
                    ["2", "C→S: HELLO", "u32 + JSON {t:HELLO, proto:1, user}"],
                    ["3", "S→C: HELLO_ACK", "{t:HELLO_ACK, proto, udp_port, fp (fingerprint Ed25519), ts}; sai phiên bản → HELLO_FAIL"],
                    ["4", "FIN", "Đóng TCP; client chuyển sang INITIAL/HANDSHAKE trên UDP (mục 2.1, 2.4)"]],
                   [1.4 * cm, 4.6 * cm, 11.0 * cm]))
    S += [Spacer(1, 3), P("HELLO không chứa mật khẩu (mật khẩu chỉ đi trong AUTH đã mã hoá AES-GCM trên UDP); "
                          "fp trong HELLO_ACK được client đối chiếu với khoá ghim (TOFU) khi bắt tay UDP.", base),
          P("2.1 Datagram (tầng transport)", h2),
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
                    ["mỗi tin nhắn", "MSG {id,to,text}  (to = tên hoặc *)", "C→S→C", "Một stream mới + FIN; server thêm from, ts, chuyển tiếp rồi ghi lịch sử"],
                    ["P2P (client ↔ client)", "FILE {id,to,name,size} · bytes thô · FILE_END {sha256}", "C↔C", "Mở trên kết nối trực tiếp giữa hai client (bắt tay X25519, đối chiếu fingerprint lấy từ PEERS); server không thấy nội dung, client gửi FILE qua server sẽ nhận ERR"]],
                   [2.8 * cm, 5.6 * cm, 1.6 * cm, 7.0 * cm]))
    S += [P("2.4 Máy trạng thái kết nối", h2),
          Preformatted("  CLIENT                                             SERVER\n"
                       "  TCP_HELLO  --[TCP] HELLO{proto,user}--------------> kiểm tra phiên bản\n"
                       "             <-[TCP] HELLO_ACK{udp_port,fp}---------- (đóng TCP)\n"
                       "  CONNECTING --INITIAL(cid,epk)--------------------> (tạo Connection, cache reply)\n"
                       "             <-HANDSHAKE(cid',epk',pk,sig)--------- \n"
                       "  (verify sig + pin) --> ESTABLISHED <-- keys (HKDF) --> ESTABLISHED\n"
                       "  AUTH (stream 0, mã hoá) ----------------------------> kiểm tra mật khẩu\n"
                       "             <-AUTH_OK + HISTORY (stream 1)------------ ONLINE  --> PEERS tới mọi người\n"
                       "  idle > 20 s hoặc CLOSE ---------------------------> OFFLINE --> PEERS cập nhật\n"
                       "  mất kết nối bất ngờ -> RECONNECTING (backoff 1,2,4..15 s) -> đăng nhập lại tự động", code)]
    S.append(PageBreak())

    # 3. Sơ đồ tuần tự
    S += [P("3. Sơ đồ tuần tự", h1), img("seq_msg.png", 16.5), Spacer(1, 8), img("seq_file.png", 16.5), PageBreak()]

    # 4. Giao diện / kiểm thử / hiệu năng
    S += [P("4. Giao diện và kết quả kiểm thử", h1),
          P("Giao diện web (HTTP + JavaScript phía client) hiển thị tin nhắn, danh sách người dùng đang online (kèm IP:port), "
            "thanh tiến trình truyền file (gửi/nhận) và chỉ số mạng thời gian thực (thuật toán CC, RTT, cwnd, gói mất).", base),
          Spacer(1, 4), img("ui_screenshot.png", 16.5), Spacer(1, 6)]
    S.append(table([["Nhóm kiểm thử", "Nội dung kiểm tra", "KQ"],
                    ["Unit", "RangeSet, mã hoá/giải mã frame, crypto (ECDH, AES-GCM chống sửa header, PBKDF2)", "OK"],
                    ["Transport", "4 MB sạch; 5% mất gói + reorder (CUBIC, BBR) – SHA-256 khớp; flow control chặn đúng cửa sổ; "
                     "từ chối server sai khoá; phát hiện ngắt kết nối", "OK"],
                    ["No-HoL", "Tin chat nhỏ trong khi file 3 MB đang truyền, 3% mất gói: độ trễ ~21 ms/tin", "OK"],
                    ["E2E (3 client)", "Đăng nhập, presence, broadcast, unicast không rò rỉ, user offline→ERR, file 3 MB qua P2P + file rỗng, client biến mất đột ngột, "
                     "đăng nhập trùng, auto-reconnect, lịch sử chat sau logout — chạy cả trên link 4% mất gói + 15 ms (BBR)", "OK"],
                    ["Gateway HTTP", "Tĩnh/API/SSE, upload stream qua POST, tải về, chặn thiếu X-Requested-With, chặn Host lạ, chặn path traversal", "OK"],
                    ["Hồi quy", "11 lỗi đã sửa: đóng nhầm kết nối NGƯỜI GỬI, hai AUTH chồng nhau, kẹt trạng thái reconnecting, ghi file nguyên tử, "
                     "Content-Length sai, tra ACK O(1), lọc BBR theo cửa sổ (so sánh với cách tính vét cạn)", "OK"],
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

    # 5. Các module chính và đoạn mã tiêu biểu
    S += [P("5. Các module chính và đoạn mã tiêu biểu", h1),
          P("Mỗi mục dưới đây ứng với một file trong <i>source/</i>: trích <b>đoạn mã quyết định hành vi</b> của file "
            "(đã rút gọn nhánh phụ và xuống dòng lại, giữ nguyên logic) rồi giải thích ngay bên dưới.", base),
          Spacer(1, 6)]

    S += [P("Cây thư mục source/", h3),
          P("Mỗi dòng là một file kèm trách nhiệm chính; số trong ngoặc là tiểu mục trích mã bên dưới. "
            "Các file __init__.py chỉ đánh dấu package nên không liệt kê.", base), Spacer(1, 3),
          Preformatted(r"""source/
|-- common/                 giao thức, transport, mã hoá dùng chung cho client + server
|   |-- packet.py           khuôn dạng datagram + frame: enc_*, decode_frames (5.1)
|   |-- protocol.py         thông điệp JSON tiền tố u32 + MsgBuffer, PROTO_VERSION, hằng số
|   |-- crypto.py           X25519 -> HKDF -> AES-256-GCM, Ed25519 ký bắt tay, PBKDF2 (5.3)
|   |-- transport.py        Connection/Endpoint: stream, ACK/SACK, mất gói, flow-control (5.5)
|   |-- congestion.py       CUBIC + BBR + RateSample (5.4)
|   |-- rangeset.py         tập số nguyên dạng khoảng: dải ACK, byte đã ACK (5.2)
|   |-- discovery.py        beacon của server + dò server trong LAN (5.6)
|   `-- fsutil.py           ghi file nguyên tử, quyền 0600 (5.7)
|-- client/
|   |-- core.py             ClientCore: bắt tay TCP, đăng nhập, reconnect, P2P file, sự kiện (5.11)
|   |-- gateway.py          HTTP/1.1: UI tĩnh, API JSON, SSE, upload/download (5.12)
|   |-- main.py             argparse + dựng event loop cho client và gateway
|   `-- web/                UI thuần JS: index.html · app.js (5.13) · style.css · fonts/
|-- server/
|   |-- server.py           Server/Session: TCP HELLO/ACK, AUTH, presence, định tuyến MSG (5.10a-b)
|   |-- users.py            UserStore: PBKDF2, first_seen.json (5.8)
|   `-- history.py          HistoryStore: history.json, debounce, for_user(since) (5.9)
|-- tests/                  7 file: transport · e2e · gateway · features · regressions · ... (5.14)
`-- docs/                   build_report.py (sinh report.pdf) · benchmark.py · ảnh PNG""", code_s), Spacer(1, 6)]

    walk = [
        ("5.1 common/packet.py — khuôn dạng datagram và frame",
         "Khai báo khuôn dạng (header 13 B + payload AES-GCM, các frame STREAM/ACK/…) và hai chiều đóng gói / bóc gói.",
         r'''def enc_ack(ranges, delay_us: int) -> bytes:
    # SACK: báo các khoảng packet number đã nhận để bên gửi chỉ gửi lại phần thiếu.
    out = bytearray(struct.pack("!BQIB", FT_ACK, ranges[0][1], delay_us, len(ranges)))
    for s, e in ranges:
        out += struct.pack("!QQ", s, e)
    return bytes(out)

# bên nhận: dữ liệu đến từ mạng nên mọi độ dài đều phải kiểm tra
if t in (FT_STREAM, FT_STREAM_FIN):
    sid, off, ln = struct.unpack_from("!IQH", buf, i + 1)
    i += STREAM_OVERHEAD
    if i + ln > n:                            # frame khai báo dài hơn số byte còn lại
        raise ValueError("truncated stream frame")
    out.append(("S", sid, off, bytes(buf[i:i + ln]), t == FT_STREAM_FIN))''',
         ["ACK mang <b>dải</b> packet number (SACK) chứ không phải từng số: 6 dải đủ mô tả hàng nghìn gói đã nhận, "
          "và bên gửi biết chính xác khoảng nào cần gửi lại.",
          "Header nằm ngoài phần mã hoá nhưng được truyền làm AAD, nên sửa dest_cid hay packet number đều làm GCM báo sai thẻ.",
          "decode_frames kiểm tra độ dài trước khi cắt buffer: frame hỏng → ValueError → kết nối đóng với "
          "lý do \"malformed frame\" thay vì đọc tràn bộ đệm."]),
        ("5.2 common/rangeset.py — tập số nguyên dạng khoảng",
         "Cấu trúc dữ liệu dùng chung cho hai việc nóng nhất của transport: sinh dải ACK (loại gói trùng/replay) "
         "và biết đoạn byte nào còn thiếu để gửi lại.",
         r'''    def add(self, s: int, e: int) -> None:
        # Thêm [s, e) và gộp với mọi khoảng chồng lấn hoặc liền kề.
        if s >= e:
            return
        out, placed = [], False
        for a, b in self.r:
            if b < s:
                out.append((a, b))
            elif a > e:
                if not placed:
                    out.append((s, e))
                    placed = True
                out.append((a, b))
            else:                        # chồng lấn hoặc liền kề -> gộp
                s, e = min(s, a), max(e, b)
        if not placed:
            out.append((s, e))
        self.r = out''',
         ["Mọi khoảng được gộp ngay khi thêm nên số khoảng rất nhỏ: mỗi thao tác O(số khoảng) chứ không O(số gói), "
          "nhờ vậy bộ nhớ không tăng khi đã nhận hàng nghìn gói.",
          "prune_oldest trả về \"mốc sàn\": packet number dưới mốc đó coi như đã thấy (chống replay), nên cửa sổ "
          "chống phát lại không phình vô hạn."]),
        ("5.3 common/crypto.py — bắt tay và mã hoá",
         "Toàn bộ bảo mật của transport nằm ở đây: X25519 → HKDF → hai khoá AES-256-GCM, Ed25519 ký transcript bắt tay.",
         r'''def derive_keys(priv, peer_pub: bytes, client_pub: bytes, server_pub: bytes):
    # HKDF tách bí mật chung X25519 thành hai khoá AES-256 độc lập, mỗi chiều một khoá.
    shared = priv.exchange(X25519PublicKey.from_public_bytes(peer_pub))
    okm = HKDF(algorithm=hashes.SHA256(), length=64, salt=client_pub + server_pub,
               info=b"collabnet-v1-keys").derive(shared)
    return okm[:32], okm[32:]

class PacketCipher:
    @staticmethod
    def _nonce(pn: int) -> bytes:
        # Nonce 96 bit: 32 bit 0 || số thứ tự gói 64 bit.
        return b"\x00\x00\x00\x00" + pn.to_bytes(8, "big")

    def seal(self, pn: int, aad: bytes, plaintext: bytes) -> bytes:
        return self._aead.encrypt(self._nonce(pn), plaintext, aad)      # aad = header''',
         ["Khoá X25519 chỉ dùng cho <b>một</b> phiên (forward secrecy): lộ khoá dài hạn về sau cũng không giải mã "
          "được lưu lượng đã ghi lại.",
          "Nonce = 0⁴ ‖ packet number và mỗi lần gửi lại dùng packet number mới, nên nonce không bao giờ trùng "
          "với cùng một khoá — điều kiện sống còn của AES-GCM.",
          "Header được xác thực như AAD: sửa bất kỳ byte nào của header (địa chỉ đích, số thứ tự) đều bị phát hiện."]),
        ("5.4 common/congestion.py — CUBIC và BBR",
         "CUBIC tăng cwnd theo hàm bậc ba của thời gian; BBR giữ BtlBw bằng bộ lọc max trên cửa sổ 10 round.",
         r'''    def on_ack(self, now, size, sent_time, rtt, sample, inflight, srtt):
        ...
        t = now - self.epoch + (srtt or 0.0)
        target = self.C * (t - self.k) ** 3 + self.w_max        # W(t) = C(t-K)^3 + Wmax
        self.w_est += 3 * (1 - self.BETA) / (1 + self.BETA) * (size / MSS) / cw
        target = min(max(target, self.w_est), 1.5 * cw)         # trần 1.5x cwnd
        if target > cw:
            inc = (target - cw) / cw * (size / MSS)
        else:
            inc = 0.01 * (size / MSS) / cw
        self.cwnd += inc * MSS

    # BBR: lọc max theo cửa sổ 10 round bằng deque đơn điệu giảm
    while self.samples and self.samples[-1][1] <= sample.rate:
        self.samples.pop()            # mẫu cũ không lớn hơn mẫu mới -> không bao giờ là max
    self.samples.append((self.round, sample.rate))
    self.btl_bw = self.samples[0][1] if self.samples else 0.0''',
         ["Ba nhánh trong on_ack: bỏ qua ACK của gói gửi trước lần mất gói gần nhất, bỏ qua khi ứng dụng không "
          "dùng hết đường (app-limited), còn lại tăng theo W(t).",
          "w_est là nhánh \"thân thiện Reno\" để CUBIC không chiếm quá nhiều khi RTT lớn; target bị kẹp trong "
          "[w_est, 1.5×cwnd] nên cwnd không nhảy vọt sau khởi động chậm.",
          "Deque đơn điệu giảm cho max cửa sổ: mỗi ACK là O(1) khấu hao thay vì quét lại toàn bộ mẫu; mẫu app-limited "
          "không được dùng để nâng BtlBw."]),
        ("5.5 common/transport.py — nhận gói và lắp gói",
         "Kết nối giữ toàn bộ trạng thái: khoá phiên, stream gửi/nhận, cửa sổ, timer. Hai đoạn dưới là chỗ dễ sai nhất.",
         r'''# (1) nhận: giải mã trước, rồi chống replay, rồi mới đổi địa chỉ peer
try:
    pt = self.recv_cipher.open(pn, hdr, ct)
except Exception:
    return                                 # gói giả mạo / hỏng -> bỏ lặng lẽ
if pn < self.recv_floor or self.recv_ranges.contains(pn):
    return                                 # gói phát lại / trùng
if addr != self.peer_addr:                 # chỉ đổi địa chỉ SAU khi giải mã thành công
    self.peer_addr = addr
self.recv_ranges.add(pn, pn + 1)
self.recv_floor = max(self.recv_floor, self.recv_ranges.prune_oldest(MAX_TRACKED_RANGES))

# (2) gửi: lắp một datagram từ nhiều stream theo (ưu tiên, lần phục vụ gần nhất)
order = sorted(self.send_streams.values(), key=lambda s: (s.priority, s.served))
for ss in order:
    fr = ss.next_frame(budget - STREAM_OVERHEAD)
    if fr is None:
        continue
    off, data, fin = fr
    parts.append(enc_stream(ss.sid, off, data, fin))
    budget -= STREAM_OVERHEAD + len(data)
    ss.served = next(self._tick)           # xoay vòng công bằng giữa các stream cùng mức''',
         ["Thứ tự mới là an toàn: giải mã → chống replay → cập nhật địa chỉ. Nếu đổi địa chỉ trước khi giải mã, "
          "kẻ giả mạo có thể \"kéo\" kết nối sang máy khác.",
          "Bộ lập lịch theo (priority, served): tin nhắn ưu tiên 0, file ưu tiên 1, cùng mức thì xoay vòng — "
          "đây là lý do chat vẫn nhanh khi file lớn đang truyền.",
          "Mất gói được phát hiện ở _detect_loss: có 3 gói gửi sau đã được ACK, hoặc quá 9/8 RTT; hết PTO thì gửi probe."]),
        ("5.6 common/discovery.py — tìm server trong LAN",
         "Server tự quảng bá để client không cần biết trước IP; đây chỉ là tiện ích, có thể tắt bằng <i>--no-beacon</i>.",
         r'''    def _tick(self):
        for dest in ("255.255.255.255", "127.0.0.1"):
            try:
                self.sock.sendto(self.msg, (dest, DISCOVERY_PORT))
            except OSError:
                pass                 # chưa có route broadcast: bỏ qua, lần sau thử lại
        self._h = self.loop.call_later(self.interval, self._tick)''',
         ["Mỗi 2 s gửi một datagram JSON tới 255.255.255.255 (trong LAN) và 127.0.0.1 (client chạy cùng máy).",
          "Phía client bind cổng 9998 với SO_REUSEADDR/SO_REUSEPORT nên nhiều client trên cùng một máy cùng nghe được beacon."]),
        ("5.7 common/fsutil.py — ghi file nguyên tử",
         "Mọi file trạng thái (users.json, first_seen.json, history.json, known_hosts.json, khoá server) đều đi qua đây.",
         r'''fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)   # mkstemp: quyền 0o600
try:
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    if mode is not None:
        os.chmod(tmp, mode)
    os.replace(tmp, path)                  # nguyên tử trên cả Windows lẫn POSIX
except BaseException:
    os.remove(tmp)                         # không để lại file tạm
    raise''',
         ["File đích luôn là bản cũ hoặc bản mới <b>hoàn chỉnh</b>: mất điện giữa chừng không để lại JSON hỏng "
          "khiến lần khởi động sau không đọc được.",
          "fsync trước khi replace nên nội dung đã xuống đĩa; quyền 0o600 giữ khoá riêng không bị người dùng khác trên máy đọc."]),
        ("5.8 server/users.py — đăng ký / đăng nhập",
         "Tài khoản lưu trong users.json dạng pbkdf2$iterations$salt$hash; tên chưa có thì đăng ký ngay lần đăng nhập đầu.",
         r'''with self.lock:
    stored = self.users.get(user)
if stored is None:
    new_hash = crypto.hash_password(password)          # PBKDF2 120k vòng, chạy NGOÀI lock
    with self.lock:
        stored = self.users.setdefault(user, new_hash)  # luồng khác có thể vừa đăng ký cùng tên
        if stored is new_hash:                          # ta là người đăng ký thành công
            atomic_write_json(self.path, self.users)
            self.first_seen[user] = time.time()
            return True, "registered"
ok = crypto.verify_password(password, stored)
return ok, "welcome back" if ok else "wrong password"''',
         ["PBKDF2 tốn hàng chục ms nên chạy ngoài lock; nếu giữ lock suốt lúc băm thì mọi lượt đăng nhập song song "
          "bị xếp hàng tuần tự.",
          "setdefault xử lý đua khi hai kết nối cùng đăng ký một tên: người thua dùng hash của người thắng.",
          "Mốc first_seen (lần đăng nhập đầu) lưu ở file riêng để users.json không phải đổi định dạng."]),
        ("5.9 server/history.py — lịch sử chat phía server",
         "Server là nguồn lưu duy nhất; client chỉ giữ bản trong RAM của phiên hiện tại.",
         r'''def add(self, rec: dict):
    self.records.append(rec)
    if len(self.records) > MAX_RECORDS:
        del self.records[:len(self.records) - MAX_RECORDS]
    if self._save_handle is None:
        self._save_handle = self.loop.call_later(1.0, self.save)   # debounce 1 s

def for_user(self, user: str, since: float = 0.0) -> list[dict]:
    for rec in reversed(self.records):
        if rec.get("to") == "*":
            if since and float(rec.get("ts") or 0) < since:
                continue                    # tin chung cũ hơn mốc tạo tài khoản
        elif rec.get("from") != user and rec.get("to") != user:
            continue''',
         ["Debounce 1 s: một đợt chat nhanh chỉ tạo một lần ghi đĩa; MAX_RECORDS = 4000 tin giữ trên đĩa.",
          "for_user trả tin chung + tin của mình + tin riêng cho mình, cũ nhất trước; since là mốc tạo tài khoản nên "
          "tài khoản mới không thấy hội thoại đã diễn ra trước khi nó tồn tại.",
          "Giới hạn 300 tin / 512 KB mỗi lần phát lại để HISTORY luôn nằm dưới giới hạn 1 MB của một thông điệp."]),
        ("5.10a server/server.py — bắt tay TCP (HELLO → HELLO_ACK)",
         "Socket TCP thô cùng số cổng với UDP; mỗi kết nối được xử lý bằng một task riêng rồi đóng ngay.",
         r'''m = await asyncio.wait_for(read_hello(), TCP_HELLO_TIMEOUT)   # 5 s
if m["t"] != "HELLO":
    raise ProtocolError(f"expected HELLO, got {m['t']}")
if m.get("proto") != PROTO_VERSION:
    await self.loop.sock_sendall(conn, pack({"t": "HELLO_FAIL", "msg": "unsupported protocol version"}))
    return
await self.loop.sock_sendall(conn, pack({"t": "HELLO_ACK", "proto": PROTO_VERSION,
                                         "udp_port": self.port, "fp": self.fingerprint, "ts": time.time()}))
...
finally:
    conn.close()                              # TCP chỉ dùng cho bước xác nhận''',
         ["Lỗi (timeout, ngắt giữa chừng, dữ liệu rác) chỉ đóng kết nối TCP đó, không ảnh hưởng server.",
          "Phía client (_tcp_handshake trong core.py) gửi HELLO, chờ HELLO_ACK, kiểm tra udp_port rồi mới gọi Endpoint.connect trên UDP.",
          "fp chỉ để kiểm tra sớm; xác thực thật vẫn là chữ ký Ed25519 trong bắt tay UDP."]),
        ("5.10b server/server.py — định tuyến tin nhắn",
         "Router: presence, chuyển tin, ghi lịch sử. Server KHÔNG nhận nội dung file.",
         r'''if hdr["t"] == "MSG":
    st.kind = "msg"
    self._route_msg(s, hdr)
elif hdr["t"] == "FILE":
    st.kind = "discard"
    self._send_ctrl(s, {"t": "ERR", "ref": str(hdr.get("id", ""))[:64],
                        "msg": "file transfer must be peer-to-peer"})
...
delivered = sum(1 for d in targets if self._deliver(d, out))
if delivered == 0 and to != "*":          # người nhận vừa rớt mạng
    self._send_ctrl(s, {"t": "ERR", "ref": mid, "msg": f"user '{to}' is not online"})
    return
if mid:                                   # giữ lại cho lần đăng nhập sau
    self.history.add({"id": mid, "from": s.user, "to": to, "text": out["text"],
                      "ts": out["ts"]})
self._send_ctrl(s, {"t": "SENT", "ref": mid, "ts": out["ts"], "n": delivered})''',
         ["Client gửi FILE qua server sẽ nhận ERR và phần thân bị bỏ (take_all) — không chuyển tiếp một byte nào, "
          "RAM server không phình theo kích thước file.",
          "Mỗi tin đi trong một stream mới nên tin nhắn không phải chờ stream khác; _deliver trả False khi đích vừa rớt.",
          "ERR khi delivered = 0 (người nhận vừa mất kết nối) để người gửi không thấy \"đã gửi\" sai; "
          "SENT chỉ gửi sau khi đã ghi lịch sử."]),
        ("5.11 client/core.py — truyền file P2P",
         "Lõi client: giữ kết nối server, mở kết nối trực tiếp tới peer khi gửi file, phát sự kiện cho UI.",
         r'''def verify(pub: bytes):
    if crypto.fingerprint(pub) != fp:
        raise ConnectionError(f"peer key mismatch for '{user}' (possible MITM)")

conn = await ep.connect(addr, verify=verify)    # bắt tay P2P + xác minh khoá người nhận
...
sid = conn.open_stream(1)                       # ưu tiên thấp hơn chat
conn.send(sid, pack({"t": "FILE", "id": fid, "from": self.user, "to": to,
                     "name": name, "size": size}))
async for chunk in chunks:
    sha.update(chunk)
    conn.send(sid, chunk)
    await conn.drain(sid)                       # back-pressure: RAM không tăng theo file
conn.send(sid, pack({"t": "FILE_END", "sha256": sha.hexdigest()}), fin=True)''',
         ["Khoá của peer lấy từ PEERS và đối chiếu fingerprint trước khi gửi byte đầu: peer giả không thể nhận file.",
          "await drain() sau mỗi mảnh là back-pressure: gateway đọc chậm lại theo mạng thay vì nạp cả file vào RAM.",
          "FILE_END mang SHA-256; bên nhận chỉ đổi tên .part thành file thật khi đủ byte và băm khớp, ngược lại xoá file tạm."]),
        ("5.12 client/gateway.py — HTTP gateway cục bộ",
         "HTTP/1.1 server tối giản trên asyncio TCP: UI tĩnh, API JSON, SSE và upload dạng stream.",
         r'''if not self._host_ok(headers.get("host", "")):
    raise HttpError(403, "bad Host header")            # chặn DNS rebinding
if method == "POST" and headers.get("x-requested-with") != "collabnet":
    raise HttpError(403, "missing X-Requested-With")   # chặn form gửi từ trang lạ
...
async def body():
    remaining = size
    while remaining > 0:
        data = await reader.read(min(65536, remaining))
        if not data:
            raise ConnectionError("upload interrupted")
        remaining -= len(data)
        yield data
fid = await self.core.send_file(to, name, size, body(), fid)''',
         ["Hai lớp chặn tấn công từ trình duyệt: Host phải là loopback (DNS rebinding) và POST phải có header riêng "
          "(form của trang khác không gắn được header này → chặn CSRF).",
          "Upload đọc 64 KB → yield → core gửi → drain(): không bước nào giữ cả file trong RAM.",
          "Mọi lỗi trả JSON {ok:false,error}; chi tiết chỉ vào log, không lộ stack trace ra trình duyệt."]),
        ("5.13 client/web/app.js — UI chỉ vẽ theo sự kiện",
         "JavaScript thuần, một kết nối SSE; tải lại trang là khôi phục trạng thái từ /api/state + HISTORY.",
         r'''function connectEvents() {
  const es = new EventSource("/api/events");
  const on = (name, fn) => es.addEventListener(name, (e) => fn(JSON.parse(e.data)));
  on("msg", (m) => { const r = addItem({ type: "msg", ...m }); ... });
  /* Lịch sử cũ do server gửi lại: thêm vào hội thoại nhưng không báo "chưa đọc". */
  on("history", (d) => { for (const m of d.items || []) addItem({ type: "msg", ...m }); });
  on("file_progress", (d) => { ... cập nhật thanh tiến trình ... });
}''',
         ["Mọi sự kiện (status, peers, msg, history, file_progress, sent, err) đi qua cùng một hàm on() nên chỉ cần "
          "một kết nối SSE cho toàn bộ giao diện.",
          "Sự kiện history thêm tin vào hội thoại nhưng không bật thông báo \"chưa đọc\", tránh nhấp nháy khi vừa đăng nhập."]),
    ]
    for title, intro, src, notes in walk:
        S += [P(title, h3), P(intro, base), Spacer(1, 2), Preformatted(src, code_s), Spacer(1, 3)]
        for n in notes:
            S.append(P("• " + n, bullet))
        S.append(Spacer(1, 7))

    S += [P("5.14 Bộ kiểm thử", h3),
          P("62 kiểm thử chia theo lớp, chạy bằng <i>python -m unittest discover -s tests -t .</i> (khoảng 2 phút):", base),
          Spacer(1, 3)]
    S.append(table([["File", "Nội dung kiểm tra"],
                    ["tests/test_transport.py", "RangeSet, mã hoá/giải mã frame, crypto; 4 MB sạch; 5% mất gói + reorder (CUBIC, BBR); flow-control; chống HoL"],
                    ["tests/test_e2e.py", "3 client thật trên loopback: login, presence, broadcast/unicast, file 3 MB qua P2P + file rỗng, mất kết nối đột ngột, biến thể 4% mất gói + 15 ms"],
                    ["tests/test_gateway.py", "HTTP thô: UI, login, chat, upload/download, SSE, thiếu X-Requested-With, Host lạ, path traversal"],
                    ["tests/test_features.py", "Trạng thái gửi, giờ server, upload bị ngắt, lịch sử khôi phục sau logout, tài khoản mới không thấy tin cũ"],
                    ["tests/test_regressions.py", "11 lỗi hồi quy (B1–B3, P1, P2, M1, D1–D3, G1) + so sánh tối ưu với cách tính vét cạn"],
                    ["tests/test_tcp_handshake.py", "HELLO → HELLO_ACK; sai phiên bản / rác không làm sập server; nhiều bắt tay TCP đồng thời; client đăng nhập luôn bắt tay TCP trước; không có TCP → lỗi rõ ràng"],
                    ["tests/test_review_fixes.py", "P2P đứt giữa chừng dọn file .part; file nhóm vẫn tới người khác khi peer đầu không với tới; chặn file-id xấu; mẫu tốc độ BBR; discovery trên Python 3.10"]],
                   [3.6 * cm, 13.4 * cm]))
    S.append(PageBreak())

    # 6. Thách thức (1 trang)
    S += [P("6. Thách thức gặp phải và cách giải quyết", h1)]
    ch = [
        ("Head-of-line blocking khi chat cùng file lớn",
         "Nếu mọi thứ nằm trong một byte-stream (như TCP) thì một gói file mất sẽ chặn cả tin nhắn. Giải pháp: transport đa stream; mỗi tin nhắn/file một stream, "
         "lập lịch ưu tiên (chat ưu tiên cao hơn file) và round-robin giữa các file. Đo được độ trễ chat ≈ 21 ms dù file đang truyền với 3% mất gói."),
        ("Mơ hồ khi đo RTT / phân biệt gửi lại",
         "Giống TCP, ACK của gói gửi lại gây nhập nhằng. Dùng số hiệu gói mới cho mọi lần gửi (kiểu QUIC) và ghi nhớ frame nào nằm trong gói nào; "
         "khi gói bị coi là mất chỉ đưa lại <i>dải byte</i> tương ứng vào hàng đợi retransmit — không gửi lại cả file."),
        ("Đề yêu cầu \"TCP socket connection + acknowledgment\" nhưng giao thức chạy trên UDP",
         "Thêm bước bắt tay TCP thật (HELLO → HELLO_ACK) cùng số cổng với UDP: client xác nhận server sống, đúng phiên bản và biết cổng UDP trước khi "
         "chuyển sang transport UDP. TCP chỉ dùng cho bước này nên không mất ưu điểm không bị Head-of-Line blocking của transport đa stream."),
        ("Phân mảnh (fragmentation) gói UDP",
         "Datagram luôn ≤ 1200 B (dưới MTU) và tự phân đoạn dữ liệu thành frame STREAM, tránh phân mảnh IP — thứ làm mất cả gói khi một mảnh mất."),
        ("Áp lực ngược khi gửi file",
         "Gateway đọc 64 KB từ trình duyệt rồi <i>await drain()</i>: drain chờ đệm gửi của stream xuống dưới ngưỡng nên RAM không tăng theo kích thước file. "
         "Lỗi thật gặp: hai tác vụ cùng chờ drain trên một stream thì callback của lần sau <b>ghi đè</b> lần trước, đệm không bao giờ được đánh thức và "
         "luồng gửi đứng vĩnh viễn khi link mất gói. Sửa bằng <i>danh sách</i> callback + đánh thức toàn bộ khi stream/kết nối đóng (phát hiện nhờ e2e có mất gói)."),
        ("Truyền file mà server không được thấy nội dung",
         "File đi trực tiếp giữa hai client: server chỉ đưa ip/port và fingerprint Ed25519 của peer trong PEERS; bên gửi đối chiếu fingerprint trước khi gửi byte "
         "đầu nên peer giả không thể nhận file, và header FILE chỉ do phía gửi tạo (bỏ header do client tự đặt qua server). Đổi lại hai client sau NAT đối xứng "
         "không kết nối được (không có relay/TURN) — ghi ở phần hạn chế."),
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
                          "chỉ hỗ trợ IPv4; cần mở cả 9000/TCP và 9000/UDP trên tường lửa. Truyền file P2P chỉ chạy khi hai client kết nối trực tiếp được với nhau "
                          "(không có relay/TURN cho NAT đối xứng), và lịch sử chat nằm trong một file JSON giới hạn 4000 tin "
                          "(mỗi lần đăng nhập chỉ phát lại 300 tin / 512 KB).", base)]

    doc = SimpleDocTemplate(os.path.join(HERE, "report.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="CollabNet - Technical Report")
    def footer(c, d):
        c.setFont("DV", 8); c.setFillColor(colors.grey)
        c.drawCentredString(A4[0] / 2, 1 * cm, f"CollabNet — Technical Explanation Report — trang {d.page}")
    doc.build(S, onFirstPage=footer, onLaterPages=footer)
    print("report.pdf written")


if __name__ == "__main__":
    build()
