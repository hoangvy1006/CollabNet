"""Sinh docs/report.pdf — báo cáo kỹ thuật CollabNet.

Nội dung bám theo mã nguồn hiện tại:
kiến trúc, phụ thuộc module, đặc tả giao thức, sơ đồ tuần tự, đoạn mã tiêu biểu, kiểm thử, hiệu năng, thách thức.

Chạy từ thư mục source/:
    python docs/build_report.py
Cần: reportlab, matplotlib, pillow. Font Lato + Noto Sans Mono nằm sẵn trong docs/fonts/ (đủ dấu tiếng Việt).
"""
import collections
import json
import os
import sys
import unittest
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                          # noqa: E402
from matplotlib import font_manager                                      # noqa: E402
from matplotlib.patches import FancyBboxPatch                            # noqa: E402
from reportlab.lib import colors                                         # noqa: E402
from reportlab.lib.enums import TA_CENTER                                # noqa: E402
from reportlab.lib.pagesizes import A4                                   # noqa: E402
from reportlab.lib.styles import ParagraphStyle                          # noqa: E402
from reportlab.lib.units import cm                                       # noqa: E402
from reportlab.pdfbase import pdfmetrics                                 # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont                             # noqa: E402
from reportlab.pdfgen import canvas as rl_canvas                         # noqa: E402
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, Image, KeepTogether,  # noqa: E402
                                NextPageTemplate, PageBreak, PageTemplate, Paragraph, Preformatted,
                                Spacer, Table, TableStyle)
from reportlab.platypus.flowables import HRFlowable                      # noqa: E402
from reportlab.platypus.tableofcontents import TableOfContents           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # source/
FONTS = os.path.join(HERE, "fonts")

# ------------------------------------------------------------------ màu & font
NAVY = "#1F3A68"
ACCENT = "#0F8B8D"
C_HTTP, C_TCP, C_UDP, C_P2P = "#6B7280", "#D97706", "#2F6FED", "#0F9D58"
C_CLIENT, C_SERVER, C_COMMON = "#2F6FED", "#0F9D58", "#7048E8"
LIGHT = {"#2F6FED": "#EAF1FE", "#0F9D58": "#E7F6EE", "#7048E8": "#F1ECFE", "#D97706": "#FDF3E3", "#6B7280": "#F2F3F5"}

pdfmetrics.registerFont(TTFont("Body", os.path.join(FONTS, "Lato-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Body-B", os.path.join(FONTS, "Lato-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Body-I", os.path.join(FONTS, "Lato-Italic.ttf")))
pdfmetrics.registerFont(TTFont("Body-K", os.path.join(FONTS, "Lato-Black.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(FONTS, "NotoSansMono-Regular.ttf")))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-B")

for f in ("Lato-Regular.ttf", "Lato-Bold.ttf", "Lato-Italic.ttf", "Lato-Black.ttf"):
    font_manager.fontManager.addfont(os.path.join(FONTS, f))
plt.rcParams["font.family"] = "Lato"


# ------------------------------------------------------------------ số liệu lấy từ mã nguồn
def load_graph():
    path = os.path.join(ROOT, "graphify-out", "graph.json")
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def count_tests():
    sys.path.insert(0, ROOT)
    try:
        suite = unittest.defaultTestLoader.discover(os.path.join(ROOT, "tests"), top_level_dir=ROOT)
        return suite.countTestCases()
    except Exception:
        return None


def loc(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


GRAPH = load_graph()
N_TESTS = count_tests() or 62
NODES_BY_FILE = collections.Counter(n.get("source_file") for n in (GRAPH or {}).get("nodes", []))


# ------------------------------------------------------------------ sơ đồ (matplotlib)
def rbox(ax, x, y, w, h, title, body="", color=C_CLIENT, fs=9.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.09",
                                fc=LIGHT.get(color, "#fff"), ec=color, lw=1.3))
    if body:
        ax.text(x + w / 2, y + h - 0.2, title, ha="center", va="top", fontsize=fs, weight="bold", color="#111")
        ax.text(x + w / 2, y + h - 0.47, body, ha="center", va="top", fontsize=fs - 1.6, color="#333", linespacing=1.35)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs, weight="bold", color="#111")


def link(ax, p, q, text="", color="#444", both=True, ls="-", fs=7.6, dy=0.1, rad=0.0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=1.3,
                                                    ls=ls, shrinkA=2, shrinkB=2, mutation_scale=9,
                                                    connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, text, ha="center", va="bottom", fontsize=fs,
                color=color, weight="bold", linespacing=1.2)


def architecture():
    fig, ax = plt.subplots(figsize=(11, 6.6))
    ax.set_xlim(0, 11); ax.set_ylim(-0.3, 6.6); ax.axis("off")
    for x0, label in ((0.1, "Máy người dùng A"), (4.05, "Server"), (7.9, "Máy người dùng B")):
        ax.add_patch(FancyBboxPatch((x0, 0.55), 3.0 if x0 != 4.05 else 2.95, 5.75,
                                    boxstyle="round,pad=0.02,rounding_size=0.12", fc="#FAFBFC", ec="#D5D9E0", lw=1, ls="--"))
        ax.text(x0 + 0.15, 6.1, label, fontsize=10.5, weight="bold", color=NAVY)
    for x0 in (0.3, 8.1):
        rbox(ax, x0, 4.85, 2.6, 1.05, "Trình duyệt", "client/web: HTML + JS thuần\nchat · file · peers · số liệu mạng", C_HTTP)
        rbox(ax, x0, 3.45, 2.6, 1.05, "HTTP Gateway (gateway.py)", "HTTP/1.1 tự viết trên asyncio\nREST · SSE · upload/download", C_TCP)
        rbox(ax, x0, 2.05, 2.6, 1.05, "ClientCore (core.py)", "TCP HELLO · AUTH · MSG · reconnect\nOutbox file · TOFU known_hosts", C_CLIENT)
        rbox(ax, x0, 0.7, 2.6, 1.0, "Transport UDP", "Endpoint → server\nP2P Endpoint (Ed25519 riêng)", C_COMMON)
        link(ax, (x0 + 1.3, 4.85), (x0 + 1.3, 4.5), color="#666")
        link(ax, (x0 + 1.3, 3.45), (x0 + 1.3, 3.1), color="#666")
        link(ax, (x0 + 1.3, 2.05), (x0 + 1.3, 1.7), color="#666")
        ax.text(x0 + 1.42, 4.6, "HTTP/SSE", fontsize=7, color=C_HTTP)
    rbox(ax, 4.2, 4.9, 2.65, 0.95, "TCP listener :9000", "HELLO → HELLO_ACK rồi đóng", C_TCP)
    rbox(ax, 4.2, 3.55, 2.65, 1.05, "Session + AUTH", "users.py: PBKDF2, tự đăng ký\npresence PEERS (ip, p2p_fp)", C_SERVER)
    rbox(ax, 4.2, 2.15, 2.65, 1.1, "Router + Lịch sử", "broadcast / unicast MSG\nhistory.json: tin + thẻ file\n(giữ tin cho người offline)", C_SERVER)
    rbox(ax, 4.2, 0.7, 2.65, 1.1, "Transport UDP :9000", "định danh Ed25519 (ký bắt tay)\nbeacon LAN :9998", C_COMMON)
    for y in (3.55, 2.15):
        link(ax, (5.52, y + 0.0), (5.52, y - 0.3), color="#666")
    # đường giữa máy
    link(ax, (2.9, 5.3), (4.2, 5.3), "TCP\nHELLO/ACK", C_TCP, both=False, dy=0.05)
    link(ax, (8.1, 5.3), (6.85, 5.3), "TCP\nHELLO/ACK", C_TCP, both=False, dy=0.05)
    link(ax, (2.9, 1.25), (4.2, 1.25), "UDP mã hoá\nAES-256-GCM", C_UDP, dy=0.05)
    link(ax, (8.1, 1.25), (6.85, 1.25), "UDP mã hoá\nAES-256-GCM", C_UDP, dy=0.05)
    ax.plot([1.6, 1.6, 9.4, 9.4], [0.7, 0.28, 0.28, 0.7], color=C_P2P, lw=1.4, ls="--")
    ax.text(5.5, -0.12, "File đi P2P trực tiếp A ↔ B (cùng transport, bên gửi kiểm fingerprint do server công bố) — server không thấy byte file",
            ha="center", fontsize=8.6, color=C_P2P, weight="bold")
    fig.savefig(os.path.join(HERE, "arch.png"), dpi=180, bbox_inches="tight"); plt.close(fig)


def module_graph():
    """Sơ đồ phụ thuộc giữa các module (cạnh import/calls/uses giữa các file, nếu có graph.json)."""
    if GRAPH is None:
        return False
    pos = {
        "client/main.py": (1.9, 5.4), "server/server.py": (7.7, 5.4),
        "client/gateway.py": (1.9, 4.2), "common/discovery.py": (4.8, 4.2), "server/users.py": (6.9, 4.2),
        "server/history.py": (9.0, 4.2),
        "client/core.py": (1.9, 3.0),
        "common/transport.py": (3.6, 1.8), "common/protocol.py": (6.2, 1.8),
        "common/congestion.py": (1.3, 0.6), "common/rangeset.py": (3.6, 0.6), "common/crypto.py": (5.9, 0.6),
        "common/fsutil.py": (8.4, 0.6), "common/packet.py": (2.45, -0.6),
    }
    nodes = {n["id"]: n for n in GRAPH["nodes"]}
    edges = set()
    for e in GRAPH["links"]:
        a, b = nodes.get(e["source"]), nodes.get(e["target"])
        if not a or not b or e.get("relation") not in ("imports", "imports_from", "calls", "uses", "inherits"):
            continue
        fa, fb = a.get("source_file"), b.get("source_file")
        if fa in pos and fb in pos and fa != fb:
            edges.add((fa, fb))
    fig, ax = plt.subplots(figsize=(10.5, 6.3))
    ax.set_xlim(0, 10.3); ax.set_ylim(-1.1, 6.0); ax.axis("off")
    col = lambda f: C_CLIENT if f.startswith("client") else C_SERVER if f.startswith("server") else C_COMMON
    w, h = 1.95, 0.62
    for a, b in sorted(edges):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        ax.annotate("", xy=(x2, y2 + (h / 2 if y2 < y1 else -h / 2 if y2 > y1 else 0)),
                    xytext=(x1, y1 - (h / 2 if y2 < y1 else -h / 2 if y2 > y1 else 0)),
                    arrowprops=dict(arrowstyle="-|>", color=col(a), lw=0.9, alpha=0.55, mutation_scale=8,
                                    shrinkA=0, shrinkB=1, connectionstyle="arc3,rad=0.06"))
    for f, (x, y) in pos.items():
        c = col(f)
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=LIGHT[c], ec=c, lw=1.3, zorder=3))
        ax.text(x, y + 0.08, f.split("/")[-1], ha="center", va="center", fontsize=9, weight="bold", zorder=4)
        ax.text(x, y - 0.15, f"{f.split('/')[0]}/ · {loc(f)} dòng",
                ha="center", va="center", fontsize=6.8, color="#444", zorder=4)
    for i, (c, t) in enumerate(((C_CLIENT, "client/"), (C_SERVER, "server/"), (C_COMMON, "common/"))):
        ax.add_patch(FancyBboxPatch((6.3 + i * 1.3, -0.85), 0.25, 0.22, boxstyle="round,pad=0.01", fc=LIGHT[c], ec=c))
        ax.text(6.62 + i * 1.3, -0.74, t, fontsize=8, va="center")
    fig.savefig(os.path.join(HERE, "modules.png"), dpi=180, bbox_inches="tight"); plt.close(fig)
    return True


KIND = {"http": C_HTTP, "tcp": C_TCP, "udp": C_UDP, "p2p": C_P2P}
KIND_LABEL = {"http": "HTTP / SSE (loopback)", "tcp": "TCP", "udp": "UDP mã hoá (client ↔ server)", "p2p": "UDP mã hoá P2P (client ↔ client)"}


def sequence(fname, title, actors, steps):
    n = len(actors)
    height = 1.55 + sum(0.5 if s[0] == "note" else 0.47 for s in steps)
    fig, ax = plt.subplots(figsize=(10.5, height))
    xs = [1.1 + i * (8.3 / (n - 1)) for i in range(n)]
    top, bottom = height - 0.55, 0.45
    ax.set_xlim(0, 10.5); ax.set_ylim(0, height); ax.axis("off")
    ax.text(0.05, height - 0.1, title, ha="left", va="top", fontsize=11, weight="bold", color=NAVY)
    for x, a in zip(xs, actors):
        c = C_HTTP if a.startswith("Browser") else C_SERVER if a == "Server" else C_CLIENT
        ax.add_patch(FancyBboxPatch((x - 0.72, top - 0.42), 1.44, 0.42, boxstyle="round,pad=0.02,rounding_size=0.07",
                                    fc=LIGHT[c], ec=c, lw=1.2))
        ax.text(x, top - 0.21, a, ha="center", va="center", fontsize=8.8, weight="bold")
        ax.plot([x, x], [bottom, top - 0.42], ls=(0, (3, 3)), c="#B5BAC3", lw=0.9)
    y = top - 0.85
    used = []
    for s in steps:
        if s[0] == "note":
            ax.text((xs[0] + xs[-1]) / 2, y, s[1], ha="center", va="center", fontsize=7.6, style="italic", color="#5B4A00",
                    bbox=dict(fc="#FFF8DB", ec="#E8C547", boxstyle="round,pad=0.3", lw=0.8))
            y -= 0.5
            continue
        a, b, txt, kind = s[:4]
        reply = len(s) > 4 and s[4]
        c = KIND[kind]
        used.append(kind)
        ax.annotate("", xy=(xs[b], y), xytext=(xs[a], y),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.3, ls="--" if reply else "-", mutation_scale=9))
        ax.text((xs[a] + xs[b]) / 2, y + 0.07, txt, ha="center", va="bottom", fontsize=8, color="#1F2328",
                bbox=dict(fc="white", ec="none", pad=0.6))
        y -= 0.47
    lx = 0.3
    for k in dict.fromkeys(used):
        ax.plot([lx, lx + 0.4], [0.15, 0.15], color=KIND[k], lw=2)
        ax.text(lx + 0.5, 0.15, KIND_LABEL[k], fontsize=7.4, va="center", color="#333")
        lx += 0.75 + 0.075 * len(KIND_LABEL[k])
    ax.plot([lx, lx + 0.4], [0.15, 0.15], color="#555", lw=1.3, ls="--")
    ax.text(lx + 0.5, 0.15, "phản hồi", fontsize=7.4, va="center", color="#333")
    fig.savefig(os.path.join(HERE, fname), dpi=180, bbox_inches="tight"); plt.close(fig)


def bench_chart(bench):
    losses = sorted({r["loss"] for r in bench})
    cub = [next(r["mbps"] for r in bench if r["loss"] == l and r["cc"] == "cubic") for l in losses]
    bbr = [next(r["mbps"] for r in bench if r["loss"] == l and r["cc"] == "bbr") for l in losses]
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    xs = range(len(losses))
    b1 = ax.bar([x - 0.19 for x in xs], cub, 0.36, color="#E08A00", label="CUBIC")
    b2 = ax.bar([x + 0.19 for x in xs], bbr, 0.36, color=C_UDP, label="BBR")
    for bars in (b1, b2):
        for r in bars:
            ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.8, f"{r.get_height():.1f}", ha="center", fontsize=8)
    ax.set_xticks(list(xs), [f"{l * 100:.0f}% mất gói" for l in losses])
    ax.set_ylabel("Thông lượng (Mbps)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E5E7EB"); ax.set_axisbelow(True)
    ax.legend(frameon=False)
    fig.savefig(os.path.join(HERE, "bench.png"), dpi=180, bbox_inches="tight"); plt.close(fig)


def make_diagrams(bench):
    architecture()
    module_graph()
    bench_chart(bench)
    sequence("seq_login.png", "Đăng nhập: bắt tay TCP → bắt tay UDP → AUTH → lịch sử", ["Browser", "Client", "Server"], [
        (0, 1, "POST /api/login {server, user, pass}", "http"),
        (1, 2, "TCP connect + HELLO {t:HELLO, proto:1, user}", "tcp"),
        (2, 1, "HELLO_ACK {proto, udp_port, fp, ts} — rồi đóng TCP", "tcp", True),
        (1, 2, "INITIAL: client_cid + X25519 public (gửi lại 0.25 → 1 s)", "udp"),
        (2, 1, "HANDSHAKE: server_cid + X25519 + Ed25519 public + chữ ký", "udp", True),
        ("note", "Client kiểm chữ ký, so fingerprint đã ghim (TOFU) → HKDF sinh 2 khoá AES-256-GCM, mỗi chiều một khoá"),
        (1, 2, "stream 0: AUTH {user, pass, p2p_port, p2p_fp}", "udp"),
        ("note", "Server chạy PBKDF2 trong executor; tên mới thì tự đăng ký; phiên cũ cùng tên bị đóng"),
        (2, 1, "stream 1: AUTH_OK {user, peers, msg, max_file} + HISTORY {items}", "udp", True),
        ("note", "Server phát PEERS mới cho mọi người đang online; client nạp outbox và đẩy file còn chờ"),
        (1, 0, "SSE: status (online) · peers · history", "http", True),
    ])
    sequence("seq_msg.png", "Tin nhắn: A gửi riêng cho B", ["Browser A", "Client A", "Server", "Client B", "Browser B"], [
        (0, 1, "POST /api/send {to: B, text}", "http"),
        ("note", "Client A mở một stream MỚI cho tin này, gói trong một datagram AES-GCM"),
        (1, 2, "STREAM(sid=n) MSG {id, to, text} + FIN", "udp"),
        (2, 1, "ACK (dải SACK)", "udp", True),
        ("note", "Server gắn from + ts (đồng hồ chung), ghi history.json — kể cả khi B đang offline"),
        (2, 3, "STREAM(sid=m) MSG {id, from: A, to, text, ts} + FIN", "udp"),
        (3, 2, "ACK", "udp", True),
        (2, 1, "ctrl: SENT {ref, ts, n}   (n = 0: B offline, tin chờ trong HISTORY)", "udp", True),
        (3, 4, "SSE: msg", "http"),
        (1, 0, "SSE: sent", "http", True),
    ])
    sequence("seq_file.png", "File: A gửi B qua P2P, server chỉ ghi thẻ file", ["Browser A", "Client A", "Server", "Client B", "Browser B"], [
        (0, 1, "POST /api/upload  (body = file, X-To, X-Filename, X-File-Id)", "http"),
        ("note", "Địa chỉ + khoá P2P của B lấy từ PEERS {ip, p2p_port, p2p_fp}; thiếu thì gửi LIST"),
        (1, 3, "INITIAL / HANDSHAKE trực tiếp — A kiểm fingerprint khoá của B", "p2p"),
        (1, 3, "STREAM (ưu tiên 1): FILE {id, from, to, name, size}", "p2p"),
        (1, 3, "dữ liệu 64 KB/lần → send → await drain()", "p2p"),
        (3, 1, "ACK + MAX_STREAM_DATA (cấp thêm credit)", "p2p", True),
        ("note", "Mỗi mảnh đồng thời ghi vào outbox/<id>.bin và cập nhật SHA-256; mất gói chỉ gửi lại dải byte thiếu"),
        (1, 3, "FILE_END {sha256} + FIN", "p2p"),
        (3, 4, "SSE: file_progress … file_received (SHA-256 khớp)", "http"),
        (1, 2, "ctrl: FILE_LOG {id, to, name, size, sha256}   — không có byte file", "udp"),
        (2, 1, "FILE_OK {ref, ts}   (thẻ file vào history.json)", "udp", True),
        ("note", "B offline: A giữ file trong outbox (file_queued); khi PEERS báo B online, A tự đẩy lại qua P2P"),
    ])


# ------------------------------------------------------------------ PDF: khung trang, mục lục, số trang
class NumberedCanvas(rl_canvas.Canvas):
    """Ghi 'Trang x / y': lưu trạng thái từng trang, tới save() mới biết tổng số trang."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._pages = []

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._pages)
        for st in self._pages:
            self.__dict__.update(st)
            if self._pageNumber > 1:
                self.setFont("Body", 8); self.setFillColor(colors.HexColor("#6B7280"))
                self.drawRightString(A4[0] - 2 * cm, 1.05 * cm, f"Trang {self._pageNumber} / {total}")
            super().showPage()
        super().save()


class Doc(BaseDocTemplate):
    def __init__(self, path, **kw):
        super().__init__(path, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2.1 * cm,
                         bottomMargin=1.9 * cm, title="CollabNet — Báo cáo Assignment 1 Mạng máy tính", author="Châu Hoàng Vỹ, Nguyễn Minh Đức", **kw)
        body = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        cover = Frame(2.3 * cm, 2.2 * cm, A4[0] - 4.6 * cm, A4[1] - 4.4 * cm, id="cover")
        self.addPageTemplates([PageTemplate("cover", [cover], onPage=draw_cover),
                               PageTemplate("body", [body], onPage=draw_page)])

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("H1", "H2"):
            level = 0 if f.style.name == "H1" else 1
            text = f.getPlainText()
            key = "h%d" % self.seq.next("toc")
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
            self.notify("TOCEntry", (level, text, self.page, key))


def draw_page(c, d):
    c.saveState()
    c.setStrokeColor(colors.HexColor("#D5D9E0")); c.setLineWidth(0.6)
    c.line(2 * cm, A4[1] - 1.45 * cm, A4[0] - 2 * cm, A4[1] - 1.45 * cm)
    c.setFont("Body-B", 8); c.setFillColor(colors.HexColor(NAVY))
    c.drawString(2 * cm, A4[1] - 1.25 * cm, "CollabNet")
    c.setFont("Body", 8); c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(2 * cm + 46, A4[1] - 1.25 * cm, "· Báo cáo kỹ thuật")
    c.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm, "Mạng máy tính · L01 · Assignment 1")
    c.line(2 * cm, 1.4 * cm, A4[0] - 2 * cm, 1.4 * cm)
    c.drawString(2 * cm, 1.05 * cm, "Distributed Streaming-based Client-Server Collaboration Application")
    c.restoreState()


def draw_cover(c, d):
    """Khung viền đôi của trang bìa (theo mẫu bìa báo cáo của trường)."""
    c.saveState()
    W, H = A4
    c.setStrokeColor(colors.HexColor(NAVY))
    c.setLineWidth(2.2); c.rect(1.4 * cm, 1.4 * cm, W - 2.8 * cm, H - 2.8 * cm)
    c.setLineWidth(0.7); c.rect(1.6 * cm, 1.6 * cm, W - 3.2 * cm, H - 3.2 * cm)
    c.restoreState()


# ------------------------------------------------------------------ PDF: kiểu chữ và khối dựng sẵn
S_BASE = ParagraphStyle("base", fontName="Body", fontSize=10, leading=14.6, textColor=colors.HexColor("#1F2328"))
S_H1 = ParagraphStyle("H1", parent=S_BASE, fontName="Body-K", fontSize=17, leading=22, spaceBefore=4, spaceAfter=2,
                      textColor=colors.HexColor(NAVY))
S_H2 = ParagraphStyle("H2", parent=S_BASE, fontName="Body-B", fontSize=12.4, leading=16, spaceBefore=11, spaceAfter=4,
                      textColor=colors.HexColor(NAVY))
S_H3 = ParagraphStyle("H3", parent=S_BASE, fontName="Body-B", fontSize=10.6, leading=14, spaceBefore=9, spaceAfter=3,
                      textColor=colors.HexColor(ACCENT))
S_CELL = ParagraphStyle("cell", parent=S_BASE, fontSize=8.7, leading=11.6)
S_CELLB = ParagraphStyle("cellb", parent=S_CELL, fontName="Body-B", textColor=colors.white)
S_CELLK = ParagraphStyle("cellk", parent=S_CELL, fontName="Body-B")
S_BUL = ParagraphStyle("bul", parent=S_BASE, fontSize=9.4, leading=13, leftIndent=12, bulletIndent=2, spaceBefore=1.5)
S_CAP = ParagraphStyle("cap", parent=S_BASE, fontName="Body-I", fontSize=8.6, leading=11, alignment=TA_CENTER,
                       textColor=colors.HexColor("#6B7280"), spaceBefore=3)
S_CODE = ParagraphStyle("code", fontName="Mono", fontSize=7.35, leading=9.4, textColor=colors.HexColor("#1F2328"))
S_LBL = ParagraphStyle("lbl", parent=S_BASE, fontName="Mono", fontSize=7.4, leading=9, textColor=colors.HexColor("#57606A"))
S_TOC1 = ParagraphStyle("toc1", parent=S_BASE, fontName="Body-B", fontSize=10.5, leading=15, spaceBefore=5)
S_TOC2 = ParagraphStyle("toc2", parent=S_BASE, fontSize=9.6, leading=13, leftIndent=16)

P = lambda t, s=S_BASE: Paragraph(t, s)


def H1(t):
    return [CondPageBreak(6 * cm), P(t, S_H1), HRFlowable(width="100%", thickness=1.6, color=colors.HexColor(ACCENT),
                                                          spaceBefore=2, spaceAfter=8)]


def bullets(items):
    return [Paragraph(t, S_BUL, bulletText="•") for t in items]


def table(rows, widths, header=True, bold_first=False):
    data = []
    for i, r in enumerate(rows):
        st = S_CELLB if header and i == 0 else S_CELL
        data.append([P(str(c), S_CELLK if (bold_first and j == 0 and st is S_CELL) else st) for j, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5D9E0")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
             ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)))
    for i in range(1 if header else 0, len(rows)):
        if (i % 2 == 0) == header:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F6F8FB")))
    t.setStyle(TableStyle(style))
    return t


def code(src, label=None, width=17 * cm):
    cell = ([P(escape(label), S_LBL), Spacer(1, 3)] if label else []) + [Preformatted(src, S_CODE)]
    t = Table([[cell]], colWidths=[width])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F8FA")),
                           ("LINEBEFORE", (0, 0), (0, -1), 2.4, colors.HexColor(ACCENT)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def callout(text, color=ACCENT, bg="#E8F6F6"):
    t = Table([[P(text, ParagraphStyle("co", parent=S_BASE, fontSize=9.3, leading=13.2))]], colWidths=[17 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(color)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def img(name, w=17, caption=None):
    from PIL import Image as PI
    path = os.path.join(HERE, name)
    iw, ih = PI.open(path).size
    out = [Image(path, width=w * cm, height=w * cm * ih / iw)]
    if caption:
        out.append(P(caption, S_CAP))
    return KeepTogether(out)


def stat_row(items):
    big = ParagraphStyle("big", parent=S_BASE, fontName="Body-K", fontSize=19, leading=22, alignment=TA_CENTER,
                         textColor=colors.HexColor(NAVY))
    small = ParagraphStyle("small", parent=S_BASE, fontSize=8.2, leading=10.5, alignment=TA_CENTER,
                           textColor=colors.HexColor("#57606A"))
    t = Table([[[P(v, big), P(k, small)] for v, k in items]], colWidths=[17 * cm / len(items)] * len(items))
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F6FB")),
                           ("LINEAFTER", (0, 0), (-2, -1), 0.6, colors.HexColor("#D5D9E0")),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return t


# ------------------------------------------------------------------ nội dung
def build():
    bench = json.load(open(os.path.join(HERE, "benchmark.json"), encoding="utf-8"))
    make_diagrams(bench)
    py_loc = sum(loc(os.path.join(d, f)) for d in ("client", "common", "server")
                 for f in os.listdir(os.path.join(ROOT, d)) if f.endswith(".py"))
    js_loc = loc("client/web/app.js")
    n_nodes = len(GRAPH["nodes"]) if GRAPH else 0
    n_edges = len(GRAPH["links"]) if GRAPH else 0

    S = []
    # ---------------- bìa
    C = lambda size, font="Body-B", color="#111111", lead=None: ParagraphStyle(
        "c%s%s" % (size, font), parent=S_BASE, fontName=font, fontSize=size, leading=lead or size * 1.3,
        alignment=TA_CENTER, textColor=colors.HexColor(color))
    S += [P("ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH", C(12.5, "Body")),
          P("TRƯỜNG ĐẠI HỌC BÁCH KHOA", C(13.5)),
          P("KHOA KHOA HỌC VÀ KỸ THUẬT MÁY TÍNH", C(13.5)),
          Spacer(1, 1.0 * cm),
          Image(os.path.join(HERE, "hcmut_logo.png"), width=4.6 * cm, height=4.6 * cm * 900 / 891),
          Spacer(1, 1.1 * cm),
          P("BÁO CÁO BÀI TẬP LỚN", C(15, "Body-B", "#333333")),
          P("MÔN: MẠNG MÁY TÍNH", C(15, "Body-B", "#333333")),
          Spacer(1, 0.55 * cm),
          HRFlowable(width="62%", thickness=1.2, color=colors.HexColor(NAVY), spaceAfter=10),
          P("ASSIGNMENT 1", C(12, "Body-B", ACCENT)),
          P("Distributed Streaming-based<br/>Client-Server Collaboration Application", C(19, "Body-K", NAVY, 25)),
          Spacer(1, 3),
          P("CollabNet — chat, phát hiện người dùng và truyền file thời gian thực trên UDP", C(11, "Body-I", "#444444")),
          HRFlowable(width="62%", thickness=1.2, color=colors.HexColor(NAVY), spaceBefore=10),
          Spacer(1, 1.1 * cm)]
    lab = ParagraphStyle("lab", parent=S_BASE, fontName="Body-B", fontSize=11.5, leading=16)
    val = ParagraphStyle("val", parent=S_BASE, fontSize=11.5, leading=16)
    info = Table([[P("Giảng viên hướng dẫn:", lab), P("Bùi Xuân Giang", val), ""],
                  [P("Lớp:", lab), P("L01", val), ""],
                  [P("Sinh viên thực hiện:", lab), P("Châu Hoàng Vỹ", val), P("MSSV: 2414064", val)],
                  ["", P("Nguyễn Minh Đức", val), P("MSSV: 2310785", val)]],
                 colWidths=[5.0 * cm, 5.0 * cm, 3.8 * cm], hAlign="CENTER")
    info.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    S += [info, Spacer(1, 1.6 * cm),
          P("Thành phố Hồ Chí Minh, tháng 11 năm 2026", C(11.5, "Body-I", "#333333")),
          NextPageTemplate("body"), PageBreak()]

    # ---------------- mục lục
    toc = TableOfContents()
    toc.levelStyles = [S_TOC1, S_TOC2]
    toc.dotsMinLevel = 0
    S += [P("Mục lục", ParagraphStyle("toct", parent=S_H1)), HRFlowable(width="100%", thickness=1.6,
                                                                       color=colors.HexColor(ACCENT), spaceAfter=8),
          toc, PageBreak()]

    # ---------------- 1. Tổng quan
    S += H1("1. Tổng quan")
    S += [P("1.1 Mục tiêu và phạm vi", S_H2),
          P("CollabNet là ứng dụng cộng tác theo mô hình client–server: người dùng đăng nhập, thấy ai đang online, "
            "chat chung hoặc riêng và gửi file cho nhau theo thời gian thực. Điểm khác biệt là toàn bộ đường truyền dữ liệu "
            "chạy trên <b>UDP thuần</b>: độ tin cậy, thứ tự, điều khiển luồng, điều khiển tắc nghẽn và mã hoá đều do chương trình "
            "tự xây dựng (tương tự ý tưởng của QUIC) thay vì dựa vào TCP hay TLS. Trước khi chuyển sang UDP, client "
            "<b>bắt tay TCP</b> với server trên cùng số cổng để xác nhận kết nối như đề yêu cầu."),
          P("Server chỉ làm ba việc: xác thực, duy trì danh sách người online và định tuyến tin nhắn (kèm lưu lịch sử). "
            "Nội dung file <b>không bao giờ đi qua server</b>: hai client kết nối thẳng với nhau (P2P) bằng chính transport đó, "
            "server chỉ công bố địa chỉ và khoá công khai của mỗi người, đồng thời ghi một \"thẻ file\" vào lịch sử."),
          Spacer(1, 4),
          table([["Hạng mục", "Nội dung"],
                 ["Thành viên", "Châu Hoàng Vỹ (2414064) · Nguyễn Minh Đức (2310785) — lớp L01"],
                 ["Ngôn ngữ", "Python 3.10+ với <b>socket</b> thô + asyncio; giao diện HTML/CSS/JavaScript thuần (không framework)"],
                 ["Thư viện ngoài", "Chỉ <i>cryptography</i> (X25519, Ed25519, HKDF, AES-256-GCM, PBKDF2). Không Flask/Django, "
                  "WebSocket, QUIC/aioquic"],
                 ["Mạng", "Bắt tay TCP HELLO → HELLO_ACK, sau đó mọi dữ liệu đi trên UDP với transport đa stream tự viết "
                  "(ACK/SACK, gửi lại chọn lọc, cửa sổ trượt, CUBIC/BBR, pacing)"],
                 ["Tính năng", "Đăng nhập/tự đăng ký, presence, chat chung + riêng, lịch sử trên server, tin cho người offline, "
                  "truyền file P2P (kể cả chat nhóm và người nhận offline), tự kết nối lại, tìm server trong LAN"],
                 ["Quy mô", f"{py_loc:,} dòng Python + {js_loc} dòng JavaScript; {N_TESTS} kiểm thử tự động".replace(",", ".")]],
                [3.4 * cm, 13.6 * cm], bold_first=True),
          Spacer(1, 6),
          callout("<b>Cấu trúc báo cáo.</b> Mục 2–4 mô tả hệ thống từ ngoài vào trong (kiến trúc → giao thức → luồng xử lý). "
                  "Mục 5 đi qua từng file mã nguồn với đoạn mã quyết định hành vi. Mục 6–7 trình bày giao diện, kiểm thử, "
                  "hiệu năng, các thách thức và hạn chế."),
          P("1.2 Ánh xạ 10 bước của đề bài", S_H2),
          P("Bảng dưới cho biết mỗi tiêu chí chấm được hiện thực ở đâu và được giải thích ở mục nào của báo cáo."),
          Spacer(1, 4)]
    S.append(table([["Bước", "Hiện thực trong CollabNet", "Mã nguồn chính", "Mục"],
                    ["1. Setup &amp; Protocol Design", "Đặc tả datagram, frame, thông điệp JSON; tách lớp mạng / dữ liệu / giao diện",
                     "common/packet.py, protocol.py", "2, 3"],
                    ["2. Client-Server Handshake", "TCP HELLO → HELLO_ACK cùng cổng, sau đó bắt tay UDP X25519 + chữ ký Ed25519",
                     "server._tcp_hello, core._tcp_handshake", "3.1, 4.1, 5.10"],
                    ["3. Authentication &amp; State", "AUTH qua kênh mã hoá, PBKDF2 + tự đăng ký, session, presence PEERS, "
                     "đăng nhập trùng đá phiên cũ, hết 10 s chưa AUTH thì đóng", "server/users.py, server.py", "3.4, 3.5, 5.8"],
                    ["4. Concurrency", "Một event loop asyncio phục vụ nhiều client và nhiều stream; PBKDF2 chạy trong executor",
                     "common/transport.py, server.py", "2.3"],
                    ["5. Streaming &amp; Routing", "Mỗi tin một stream, ưu tiên chat hơn file, broadcast/unicast, giờ server, "
                     "giữ tin cho người offline", "server._route_msg, history.py", "4.2, 5.5, 5.10"],
                    ["6. Reliable File Transfer", "P2P trực tiếp, SACK + gửi lại chọn lọc, flow control, SHA-256, outbox cho người offline",
                     "client/core.py", "4.3, 5.11"],
                    ["7. Resilience &amp; Errors", "Phát hiện mất gói, CUBIC/BBR, keep-alive 4 s, idle 20 s, reconnect backoff, "
                     "đổi địa chỉ (migration)", "transport.py, congestion.py", "5.4, 5.5, 7"],
                    ["8. Security Layer", "X25519 → HKDF → AES-256-GCM, ký Ed25519 + ghim khoá TOFU, header là AAD, chống replay; "
                     "gateway chặn DNS rebinding/CSRF", "common/crypto.py, gateway.py", "5.3, 5.12"],
                    ["9. HTTP UI + JavaScript", "HTTP/1.1 tự viết: REST + SSE + upload dạng stream; UI JS thuần",
                     "client/gateway.py, web/app.js", "6.1, 5.12, 5.13"],
                    ["10. Testing &amp; Quality", f"{N_TESTS} kiểm thử tự động, kiểm thử hồi quy, benchmark",
                     "tests/, docs/benchmark.py", "6.2, 6.3"]],
                   [3.6 * cm, 7.4 * cm, 4.2 * cm, 1.8 * cm], bold_first=True))

    # ---------------- 2. Kiến trúc
    S += [PageBreak()] + H1("2. Kiến trúc hệ thống")
    S += [P("2.1 Sơ đồ tổng thể", S_H2),
          P("Mỗi máy người dùng chạy một tiến trình client gồm ba lớp: <b>giao diện</b> (trình duyệt, chỉ nói HTTP với gateway "
            "cục bộ trên 127.0.0.1), <b>lõi client</b> (ClientCore: phiên làm việc, tin nhắn, file) và <b>transport UDP</b>. "
            "Server có cấu trúc tương tự nhưng thay giao diện bằng trình quản lý phiên và bộ định tuyến."),
          Spacer(1, 4),
          img("arch.png", 17, "Hình 1. Kiến trúc CollabNet: TCP chỉ dùng cho bước xác nhận, mọi dữ liệu đi trên UDP mã hoá; file đi P2P."),
          Spacer(1, 6)]
    S.append(table([["Lớp", "Trách nhiệm", "File"],
                    ["Giao diện", "Vẽ hội thoại, danh sách online, tiến trình file, số liệu mạng; nhận sự kiện qua SSE",
                     "client/web/index.html, app.js, style.css"],
                    ["Gateway", "Cầu nối HTTP ↔ ClientCore: phục vụ file tĩnh, API JSON, SSE, upload/download dạng stream",
                     "client/gateway.py"],
                    ["Logic mạng", "Phiên với server, P2P, outbox, định tuyến, presence, lịch sử",
                     "client/core.py, server/server.py"],
                    ["Transport", "Kết nối, stream, ACK/SACK, mất gói, cửa sổ, tắc nghẽn, mã hoá gói",
                     "common/transport.py, congestion.py, rangeset.py"],
                    ["Dữ liệu", "Khuôn dạng gói/frame, thông điệp JSON, mật mã, lưu trữ nguyên tử",
                     "common/packet.py, protocol.py, crypto.py, fsutil.py; server/users.py, history.py"]],
                   [2.6 * cm, 8.6 * cm, 5.8 * cm], bold_first=True))

    if os.path.exists(os.path.join(HERE, "modules.png")):
        S += [P("2.2 Phụ thuộc giữa các module", S_H2),
              P("Mỗi mũi tên là một quan hệ import / gọi hàm giữa hai file. Phụ thuộc chỉ đi một chiều từ client/ và server/ "
                "xuống common/, không có vòng import, và client với server không import lẫn nhau: hai bên chỉ chia sẻ "
                "giao thức đặt trong common/."),
              Spacer(1, 4),
              img("modules.png", 16.5, "Hình 2. Phụ thuộc giữa các module mã nguồn (kèm số dòng của mỗi file)."),
              ]

    S += [P("2.3 Mô hình đồng thời", S_H2),
          P("Cả client và server chạy trên <b>một event loop asyncio</b> (SelectorEventLoop, dùng được trên cả Windows). "
            "Mỗi kết nối UDP là một đối tượng <i>Connection</i> do <i>Endpoint</i> phân phối theo connection id; trong một kết nối "
            "có nhiều stream độc lập. Vì vậy server phục vụ nhiều client cùng lúc mà không cần một luồng cho mỗi client, "
            "và tin chat không phải chờ file đang truyền. Hai chỗ có thể chặn event loop được xử lý riêng:"),
          ] + bullets([
              "Băm mật khẩu PBKDF2 (hàng chục ms) chạy trong <i>run_in_executor</i>; UserStore dùng khoá luồng và "
              "<i>setdefault</i> để hai lượt đăng ký cùng tên chỉ có một người thắng.",
              "Ghi đĩa (lịch sử, tài khoản, outbox) đi qua <i>atomic_write</i> và được gom (debounce 1 s) để một đợt chat nhanh "
              "chỉ ghi một lần.",
              "Bên gửi dữ liệu lớn luôn <i>await drain()</i>: khi đệm gửi của stream vượt 256 KB thì chờ tới khi xuống dưới 64 KB "
              "(back-pressure), nên RAM không tăng theo kích thước file.",
          ])

    S += [P("2.4 Quyết định thiết kế chính", S_H2)]
    S.append(table([["Vấn đề", "Giải pháp trong CollabNet", "Liên hệ lý thuyết"],
                    ["Kết nối + xác nhận (bước 2)", "Client kết nối TCP tới server cùng số cổng với UDP, gửi HELLO; server trả HELLO_ACK "
                     "{udp_port, fp} rồi đóng TCP", "TCP 3-way handshake, socket API"],
                    ["Tin cậy trên UDP", "Packet number tăng đơn điệu (gửi lại dùng số mới), ACK dạng dải (SACK), mất gói khi có 3 gói "
                     "sau được ACK hoặc quá 9/8 RTT, PTO gửi probe", "rdt, Selective Repeat, ước lượng RTT"],
                    ["Không Head-of-Line blocking", "Mỗi tin nhắn / mỗi file là một stream; chỉ byte trong cùng stream mới phải đúng thứ tự",
                     "HTTP/2 → HTTP/3, QUIC"],
                    ["Điều khiển luồng", "Cửa sổ nhận 512 KB mỗi stream, trượt bằng MAX_STREAM_DATA; tối đa 1024 stream nhận",
                     "flow control, rwnd"],
                    ["Điều khiển tắc nghẽn", "CUBIC (mặc định) hoặc BBR (<i>--cc bbr</i>) + pacing; cwnd ban đầu 10 MSS",
                     "AIMD, CUBIC, BBR"],
                    ["Bảo mật", "X25519 tạm thời → HKDF → 2 khoá AES-256-GCM; server ký transcript bằng Ed25519, client ghim "
                     "fingerprint (TOFU); header là AAD; cửa sổ chống replay", "DH, chữ ký số, MITM, TLS 1.3"],
                    ["Phát hiện / presence", "Beacon UDP 2 s/lần trên cổng 9998; server đẩy PEERS mỗi khi có người vào/ra",
                     "broadcast, dịch vụ thư mục"],
                    ["Truyền file", "P2P trực tiếp; server công bố ip, p2p_port, p2p_fp; bên gửi kiểm fingerprint trước byte đầu",
                     "mô hình ngang hàng, xác thực khoá"],
                    ["Người nhận offline", "Tin: server lưu và gửi lại trong HISTORY. File: bên gửi giữ trong outbox, server ghi thẻ "
                     "FILE_LOG; đẩy P2P khi người nhận online", "store-and-forward"]],
                   [3.4 * cm, 9.3 * cm, 4.3 * cm], bold_first=True))

    # ---------------- 3. Giao thức
    S += [PageBreak()] + H1("3. Đặc tả giao thức")
    S += [P("3.1 Bắt tay TCP (kết nối và xác nhận)", S_H2),
          P("Server mở socket TCP và UDP <b>cùng số cổng</b> (mặc định 9000). Lúc đăng nhập, client làm bước này trước tiên; "
            "nếu không kết nối được TCP, client báo lỗi rõ ràng (<i>cannot reach server over TCP …</i>) và không thử UDP. "
            "Mỗi lượt có giới hạn 5 s (TCP_HELLO_TIMEOUT)."),
          Spacer(1, 3)]
    S.append(table([["Bước", "Gói tin", "Nội dung"],
                    ["1", "TCP SYN → SYN/ACK → ACK", "Bắt tay 3 bước của hệ điều hành (sock_connect)"],
                    ["2", "C → S: HELLO", "u32 độ dài + JSON {t: HELLO, proto: 1, user}"],
                    ["3", "S → C: HELLO_ACK", "{t: HELLO_ACK, proto, udp_port, fp (fingerprint Ed25519), ts}; sai phiên bản → HELLO_FAIL"],
                    ["4", "FIN", "Đóng TCP; client kiểm udp_port rồi chuyển sang INITIAL/HANDSHAKE trên UDP"]],
                   [1.3 * cm, 4.2 * cm, 11.5 * cm]))
    S += [Spacer(1, 4),
          callout("HELLO không chứa mật khẩu: mật khẩu chỉ đi trong AUTH đã mã hoá AES-GCM trên UDP. Trường <i>fp</i> chỉ để kiểm "
                  "tra sớm; xác thực thật vẫn là chữ ký Ed25519 trong bắt tay UDP."),
          P("3.2 Datagram (tầng transport)", S_H2),
          code("+------+----------+----------------+------------------------------+---------+\n"
               "| type | dest_cid | packet number  |  frames, mã hoá AES-256-GCM  | GCM tag |\n"
               "| 1 B  |   4 B    |      8 B       |          <= 1171 B           |  16 B   |\n"
               "+------+----------+----------------+------------------------------+---------+\n"
               " \\____ header 13 B (xác thực làm AAD) ___/          tổng datagram <= 1200 B", "common/packet.py"),
          Spacer(1, 5)]
    S.append(table([["type", "Ý nghĩa", "Nội dung"],
                    ["0x01 INITIAL", "Chào của client (rõ)", "client_cid (4) + X25519 public (32); gửi lại với backoff 0.25 → 1 s"],
                    ["0x02 HANDSHAKE", "Chào của bên nhận (rõ)", "server_cid (4) + X25519 public (32) + Ed25519 public (32) + chữ ký (64) trên transcript"],
                    ["0x10 DATA", "Gói ứng dụng", "pn (8) tăng đơn điệu; nonce = 0⁴ ‖ pn; mỗi chiều một khoá"]],
                   [3.1 * cm, 3.6 * cm, 10.3 * cm]))
    S += [P("3.3 Frame (bên trong gói DATA đã giải mã)", S_H2)]
    S.append(table([["Frame", "Trường", "Mục đích"],
                    ["STREAM 0x02 / 0x03 (FIN)", "stream_id (4) offset (8) length (2) data", "Dữ liệu theo byte-offset; FIN đánh dấu hết stream"],
                    ["ACK 0x04", "largest (8) delay_us (4) n (1) n × [start (8) end (8)]", "SACK: tối đa 6 dải packet number đã nhận"],
                    ["MAX_STREAM_DATA 0x05", "stream_id (4) max_offset (8)", "Cấp thêm credit (cửa sổ trượt) cho bên gửi"],
                    ["PING 0x06", "—", "Keep-alive 4 s khi rảnh; probe khi hết PTO"],
                    ["CLOSE 0x07", "code (2) len (2) reason", "Đóng kết nối có lý do"]],
                   [4.2 * cm, 6.4 * cm, 6.4 * cm]))
    S += [P("3.4 Thông điệp ứng dụng", S_H2),
          P("Mỗi thông điệp là <b>u32 độ dài + JSON UTF-8</b>, luôn có trường <b>t</b>; tối đa 1 MB một thông điệp, văn bản chat "
            "tối đa 8192 ký tự. Stream 0 (client mở) và stream 1 (server mở) là kênh điều khiển; mỗi tin nhắn và mỗi file dùng "
            "một stream mới."),
          Spacer(1, 3)]
    S.append(table([["Kênh", "Thông điệp", "Hướng", "Ý nghĩa"],
                    ["ctrl", "AUTH {user, pass, p2p_port, p2p_fp}", "C → S", "Đăng nhập; tên mới tự đăng ký (PBKDF2-SHA256 + salt). "
                     "Kèm cổng và fingerprint P2P để người khác gửi file trực tiếp"],
                    ["ctrl", "AUTH_OK {user, peers, msg, max_file} · AUTH_FAIL {msg}", "S → C", "Kết quả đăng nhập; max_file mặc định 512 MB"],
                    ["ctrl", "HISTORY {items}", "S → C", "Ngay sau AUTH_OK: tin chung + tin của mình + thẻ file (tối đa 300 mục / 512 KB)"],
                    ["ctrl", "LIST → PEERS {peers: [{user, ip, port, since, p2p_port, p2p_fp}]}", "C ↔ S", "Presence; server tự đẩy PEERS khi có người vào/ra"],
                    ["stream mới", "MSG {id, to, text}  (to = tên hoặc *)", "C → S → C", "Server thêm from, ts rồi chuyển tiếp và ghi lịch sử"],
                    ["ctrl", "SENT {ref, ts, n} · ERR {ref, msg}", "S → C", "n = số người đã nhận ngay (0 nếu người nhận offline, tin vẫn được giữ); "
                     "ERR khi tên người nhận không tồn tại"],
                    ["ctrl", "FILE_LOG {id, to, name, size, sha256} → FILE_OK {ref, ts}", "C ↔ S", "Ghi thẻ file vào lịch sử (không có byte file); "
                     "kiểm size ≤ max_file, sha256 hợp lệ, người nhận tồn tại; gửi lại cùng id không ghi trùng"],
                    ["P2P stream", "FILE {id, from, to, name, size} · byte thô · FILE_END {sha256}", "C ↔ C", "Nội dung file trên kết nối "
                     "trực tiếp; client lỡ gửi FILE qua server sẽ nhận ERR và phần thân bị bỏ"],
                    ["ctrl", "BYE", "C → S", "Đăng xuất"]],
                   [2.2 * cm, 5.9 * cm, 1.9 * cm, 7.0 * cm]))
    S += [P("3.5 Máy trạng thái kết nối", S_H2),
          code("  CLIENT                                                  SERVER\n"
               "  TCP_HELLO   --[TCP] HELLO {proto, user}-------------->  kiểm tra phiên bản\n"
               "              <-[TCP] HELLO_ACK {udp_port, fp}----------  (đóng TCP)\n"
               "  CONNECTING  --INITIAL (cid, epk)--------------------->  tạo Connection, cache trả lời\n"
               "              <-HANDSHAKE (cid', epk', pk, sig)---------\n"
               "  verify sig + pin --> ESTABLISHED  <-- khoá HKDF -->  ESTABLISHED (10 s để AUTH)\n"
               "  AUTH (stream 0, mã hoá) ----------------------------->  PBKDF2 / tự đăng ký\n"
               "              <-AUTH_OK + HISTORY (stream 1)------------  ONLINE --> PEERS tới mọi người\n"
               "  idle > 20 s hoặc CLOSE ----------------------------->  OFFLINE --> PEERS cập nhật\n"
               "  mất kết nối bất ngờ -> RECONNECTING (backoff 1, 2, 4 .. 15 s) -> đăng nhập lại tự động",
               "trạng thái phía client và server")]

    # ---------------- 4. Luồng xử lý
    S += [PageBreak()] + H1("4. Luồng xử lý chính")
    S += [P("4.1 Đăng nhập", S_H2),
          img("seq_login.png", 16.5, "Hình 3. Từ lúc bấm Đăng nhập tới khi giao diện có danh sách online và lịch sử."),
          P("4.2 Tin nhắn", S_H2),
          img("seq_msg.png", 16.5, "Hình 4. Một tin riêng từ A tới B; tin chung (to = *) giống hệt nhưng server gửi cho mọi người trừ A."),
          P("4.3 Truyền file P2P và giao cho người offline", S_H2),
          img("seq_file.png", 16.5, "Hình 5. Byte file chỉ đi giữa hai client; server chỉ giữ thẻ file để người nhận thấy trong lịch sử."),
          Spacer(1, 4)]
    S += bullets([
        "<b>Chat chung (to = *)</b>: bên gửi mở một kết nối P2P tới <i>từng</i> người đang online. Nếu người đầu tiên không kết nối "
        "được, lượt gửi không bị huỷ: file vẫn được lưu vào outbox và đẩy cho những người còn lại.",
        "<b>Người nhận offline</b>: file nằm trong <i>client_state/outbox/</i> của bên gửi kèm <i>index.json</i> ghi ai đã nhận. "
        "Khi PEERS báo người đó online (hoặc khi bên gửi đăng nhập lại), <i>_flush_all</i> tự đẩy file. Với chat riêng, file trong "
        "outbox bị xoá ngay khi người nhận đã có; với chat chung thì được giữ lại cho những người còn offline.",
        "<b>Bên nhận</b> ghi vào <i>.part</i>, chỉ đổi thành file thật khi đủ byte và SHA-256 khớp; đứt giữa chừng thì xoá file tạm "
        "và báo lỗi cho cả hai phía.",
    ])

    # ---------------- 5. Module
    S += [PageBreak()] + H1("5. Các module chính và đoạn mã tiêu biểu")
    S += [P("Mỗi tiểu mục ứng với một file trong <i>source/</i>: trích <b>đoạn mã quyết định hành vi</b> (đã rút gọn nhánh phụ, giữ "
            "nguyên logic) rồi giải thích ngay bên dưới. Cây thư mục cho biết vị trí từng file; số trong ngoặc là tiểu mục tương ứng."),
          Spacer(1, 4),
          code(r"""source/
|-- common/               giao thức, transport, mật mã dùng chung cho client + server
|   |-- packet.py         khuôn dạng datagram + frame: enc_*, decode_frames            (5.1)
|   |-- rangeset.py       tập số nguyên dạng khoảng: dải ACK, byte đã ACK              (5.2)
|   |-- crypto.py         X25519 -> HKDF -> AES-256-GCM, Ed25519, PBKDF2               (5.3)
|   |-- congestion.py     CUBIC + BBR + RateSample                                     (5.4)
|   |-- transport.py      Endpoint / Connection: stream, ACK/SACK, mất gói, cửa sổ     (5.5)
|   |-- discovery.py      beacon của server + dò server trong LAN                      (5.6)
|   |-- fsutil.py         ghi file nguyên tử, quyền 0600                               (5.7)
|   `-- protocol.py       JSON tiền tố u32 + MsgBuffer, PROTO_VERSION, safe_filename
|-- server/
|   |-- users.py          UserStore: PBKDF2, tự đăng ký, first_seen.json               (5.8)
|   |-- history.py        HistoryStore: history.json, debounce, for_user(since)        (5.9)
|   |-- server.py         TCP HELLO/ACK, AUTH, presence, định tuyến MSG, FILE_LOG     (5.10)
|   `-- reset.py          xoá tài khoản + lịch sử trước buổi demo (kiểm cổng đang mở)
|-- client/
|   |-- core.py           ClientCore: bắt tay TCP, đăng nhập, reconnect, P2P, outbox  (5.11)
|   |-- gateway.py        HTTP/1.1: UI tĩnh, API JSON, SSE, upload/download            (5.12)
|   |-- main.py           tham số dòng lệnh, dựng event loop cho core + gateway
|   `-- web/              index.html · app.js (5.13) · style.css · fonts/ (Be Vietnam Pro)
|-- tests/                7 file kiểm thử                                             (5.14)
`-- docs/                 benchmark.py (đo CUBIC / BBR) · sơ đồ và báo cáo""", "cây thư mục"),
          ]

    walk = [
        ("5.1 common/packet.py — khuôn dạng datagram và frame",
         "Khai báo header 13 B, các loại gói, các frame STREAM/ACK/… và hai chiều đóng gói / bóc gói.",
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
         ["ACK mang <b>dải</b> packet number chứ không phải từng số: 6 dải đủ mô tả hàng nghìn gói, và bên gửi biết chính xác "
          "khoảng nào cần gửi lại.",
          "Header nằm ngoài phần mã hoá nhưng được truyền làm AAD, nên sửa dest_cid hay packet number đều làm GCM báo sai thẻ.",
          "decode_frames kiểm tra độ dài trước khi cắt buffer: frame hỏng → ValueError → kết nối đóng với lý do "
          "\"malformed frame\" thay vì đọc tràn bộ đệm."]),
        ("5.2 common/rangeset.py — tập số nguyên dạng khoảng",
         "Cấu trúc dữ liệu cho hai việc nóng nhất của transport: sinh dải ACK (loại gói trùng / phát lại) và biết đoạn byte nào "
         "còn thiếu để gửi lại.",
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
         ["Khoảng được gộp ngay khi thêm nên số khoảng rất nhỏ: mỗi thao tác là O(số khoảng) chứ không O(số gói).",
          "prune_oldest trả về \"mốc sàn\": packet number dưới mốc đó coi như đã thấy (chống replay), nên cửa sổ chống phát lại "
          "không phình vô hạn (giữ tối đa 64 khoảng)."]),
        ("5.3 common/crypto.py — bắt tay và mã hoá",
         "Toàn bộ bảo mật của transport: X25519 → HKDF → hai khoá AES-256-GCM, Ed25519 ký transcript bắt tay.",
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
         ["Khoá X25519 chỉ dùng cho <b>một</b> phiên (forward secrecy): lộ khoá dài hạn về sau cũng không giải mã được lưu "
          "lượng đã ghi lại.",
          "Nonce = 0⁴ ‖ packet number và mỗi lần gửi lại dùng packet number mới, nên nonce không bao giờ lặp với cùng một khoá — "
          "điều kiện sống còn của AES-GCM.",
          "Client P2P cũng có định danh Ed25519 riêng (client_identity.key); fingerprint của nó được công bố qua AUTH → PEERS."]),
        ("5.4 common/congestion.py — CUBIC và BBR",
         "CUBIC tăng cwnd theo hàm bậc ba của thời gian; BBR ước lượng băng thông nút cổ chai bằng bộ lọc max trên cửa sổ 10 round.",
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
         ["w_est là nhánh \"thân thiện Reno\" để CUBIC không lép vế khi RTT nhỏ; target bị kẹp trong [w_est, 1.5×cwnd] "
          "nên cwnd không nhảy vọt.",
          "Deque đơn điệu giảm cho max cửa sổ: mỗi ACK là O(1) khấu hao thay vì quét lại toàn bộ mẫu; mẫu app-limited không "
          "được dùng để nâng BtlBw.",
          "Mẫu tốc độ giao hàng (RateSample) tính thời gian ACK từ <i>delivered_time</i> của gói; trước khi sửa giá trị này luôn bằng 0 "
          "khiến BBR ước lượng băng thông quá cao (có kiểm thử hồi quy)."]),
        ("5.5 common/transport.py — nhận gói và lắp gói",
         "Connection giữ toàn bộ trạng thái một kết nối: khoá phiên, stream gửi/nhận, cửa sổ, timer. Hai đoạn dưới là chỗ dễ sai nhất.",
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
         ["Thứ tự an toàn: giải mã → chống replay → cập nhật địa chỉ. Nếu đổi địa chỉ trước khi giải mã, kẻ giả mạo có thể "
          "\"kéo\" kết nối sang máy khác. Đổi địa chỉ hợp lệ chính là connection migration (đổi mạng / NAT rebinding).",
          "Bộ lập lịch theo (priority, served): tin nhắn ưu tiên 0, file ưu tiên 1, cùng mức thì xoay vòng — vì vậy chat vẫn nhanh "
          "khi file lớn đang truyền.",
          "Mất gói được phát hiện khi có 3 gói gửi sau đã được ACK hoặc quá 9/8 RTT; hết PTO thì gửi probe; rảnh 4 s gửi PING, "
          "im lặng quá 20 s thì đóng kết nối."]),
        ("5.6 common/discovery.py — tìm server trong LAN",
         "Server tự quảng bá để client không cần biết trước IP; có thể tắt bằng <i>--no-beacon</i>. Giao diện gọi <i>/api/discover</i>.",
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
         "Mọi file trạng thái (users.json, first_seen.json, history.json, known_hosts.json, outbox/index.json, khoá) đi qua đây.",
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
         ["File đích luôn là bản cũ hoặc bản mới <b>hoàn chỉnh</b>: mất điện giữa chừng không để lại JSON hỏng.",
          "fsync trước khi replace nên nội dung đã xuống đĩa; quyền 0o600 giữ khoá riêng không bị người dùng khác đọc."]),
        ("5.8 server/users.py — đăng ký / đăng nhập",
         "Tài khoản lưu trong users.json dạng pbkdf2$iterations$salt$hash; tên chưa có thì đăng ký ngay lần đăng nhập đầu.",
         r'''with self.lock:
    stored = self.users.get(user)
if stored is None:
    new_hash = crypto.hash_password(password)          # PBKDF2, chạy NGOÀI lock
    with self.lock:
        stored = self.users.setdefault(user, new_hash)  # luồng khác có thể vừa đăng ký cùng tên
        if stored is new_hash:                          # ta là người đăng ký thành công
            atomic_write_json(self.path, self.users)
            self.first_seen[user] = time.time()
            return True, "registered"
ok = crypto.verify_password(password, stored)
return ok, "welcome back" if ok else "wrong password"''',
         ["PBKDF2 tốn hàng chục ms nên chạy ngoài lock; nếu giữ lock suốt lúc băm thì mọi lượt đăng nhập song song bị xếp hàng.",
          "setdefault xử lý đua khi hai kết nối cùng đăng ký một tên: người thua dùng hash của người thắng.",
          "Tên người dùng phải khớp <i>^[A-Za-z0-9_.-]{2,24}$</i>; first_seen (mốc tạo tài khoản) lưu ở file riêng."]),
        ("5.9 server/history.py — lịch sử chat phía server",
         "Server là nơi lưu duy nhất cho tin nhắn và thẻ file; client chỉ giữ bản trong RAM của phiên hiện tại.",
         r'''def add(self, rec: dict):
    self.records.append(rec)
    if len(self.records) > MAX_RECORDS:                    # 4000 mục
        del self.records[:len(self.records) - MAX_RECORDS]
    if self._save_handle is None:
        self._save_handle = self.loop.call_later(1.0, self.save)   # debounce 1 s

def for_user(self, user: str, since: float = 0.0) -> list[dict]:
    for rec in reversed(self.records):
        if rec.get("to") == "*":
            if since and float(rec.get("ts") or 0) < since:
                continue                    # tin chung cũ hơn mốc tạo tài khoản
        elif rec.get("from") != user and rec.get("to") != user:
            continue
        ...                                 # dừng khi quá 300 mục hoặc 512 KB''',
         ["for_user trả tin chung + tin của mình + tin riêng cho mình, cũ nhất trước; tài khoản mới không thấy hội thoại chung "
          "diễn ra trước khi nó tồn tại.",
          "Bản ghi có <i>kind: file</i> là thẻ file (tên, kích thước, sha256) — giao diện vẽ thành thẻ tải về, còn byte thì "
          "đi P2P.",
          "Giới hạn 300 mục / 512 KB mỗi lần phát lại để HISTORY luôn dưới giới hạn 1 MB của một thông điệp."]),
        ("5.10 server/server.py — bắt tay TCP, định tuyến, thẻ file",
         "Server gồm listener TCP cho HELLO, Endpoint UDP cho phiên mã hoá, và các hàm xử lý theo loại thông điệp.",
         r'''# (a) TCP: HELLO -> HELLO_ACK rồi đóng, lỗi chỉ ảnh hưởng kết nối đó
m = await asyncio.wait_for(read_hello(), TCP_HELLO_TIMEOUT)   # 5 s
if m.get("proto") != PROTO_VERSION:
    await self.loop.sock_sendall(conn, pack({"t": "HELLO_FAIL", "msg": "unsupported protocol version"}))
    return
await self.loop.sock_sendall(conn, pack({"t": "HELLO_ACK", "proto": PROTO_VERSION,
                                         "udp_port": self.port, "fp": self.fingerprint, "ts": time.time()}))

# (b) định tuyến MSG: người nhận phải tồn tại; offline thì vẫn lưu
if to == "*":
    targets = [d for u, d in self.by_user.items() if u != s.user]
elif to != s.user and self.store.has_user(to):
    dest = self.by_user.get(to)                    # None nếu người nhận đang offline
    targets = [dest] if dest is not None else []
else:
    self._send_ctrl(s, {"t": "ERR", "ref": mid, "msg": f"user '{to}' is not online"})
    return
delivered = sum(1 for d in targets if self._deliver(d, out))
if mid:                                            # giao lại qua HISTORY khi họ đăng nhập
    self.history.add({"id": mid, "from": s.user, "to": to, "text": out["text"], "ts": out["ts"]})
self._send_ctrl(s, {"t": "SENT", "ref": mid, "ts": out["ts"], "n": delivered})

# (c) FILE_LOG: chỉ ghi thẻ file, không có byte nào
if size < 0 or (self.max_file and size > self.max_file):
    self._send_ctrl(s, {"t": "ERR", "ref": fid, "msg": "invalid or too large file"})
    return
if any(r.get("id") == fid for r in self.history.records):
    self._send_ctrl(s, {"t": "FILE_OK", "ref": fid, "ts": time.time()})    # idempotent
    return''',
         ["TCP chỉ dùng cho bước xác nhận; mọi lỗi (timeout, ngắt giữa chừng, dữ liệu rác) chỉ đóng kết nối TCP đó, server "
          "không bị ảnh hưởng (có kiểm thử nhiều bắt tay TCP đồng thời).",
          "SENT trả <i>n</i> = số người đã nhận ngay; n = 0 nghĩa là người nhận offline và tin chờ trong lịch sử. ERR chỉ xuất hiện "
          "khi tên người nhận không tồn tại (hoặc gửi cho chính mình).",
          "Stream mở bằng FILE (client cũ) nhận ERR \"file transfer must be peer-to-peer\" và phần thân bị bỏ bằng take_all — "
          "RAM server không phình theo kích thước file.",
          "Mỗi session tối đa 64 stream đang mở; chưa AUTH sau 10 s thì đóng (\"auth timeout\")."]),
        ("5.11 client/core.py — P2P và outbox",
         "Lõi client: giữ kết nối server, mở kết nối trực tiếp tới peer khi gửi file, giữ outbox cho người offline, phát sự kiện cho UI.",
         r'''def verify(pub: bytes):                         # bắt tay P2P: khoá phải khớp fingerprint server công bố
    if crypto.fingerprint(pub) != fp:
        raise ConnectionError(f"peer key mismatch for '{user}' (possible man-in-the-middle)")
conn = await ep.connect(addr, verify=verify)

# gửi: mỗi mảnh vừa đi P2P vừa ghi vào outbox, cùng lúc tính SHA-256
with open(path, "wb") as fh:                    # path = outbox/<fid>.bin
    async for chunk in chunks:
        sha.update(chunk)
        fh.write(chunk)
        if conn is not None:
            conn.send(sid, chunk)
            await conn.drain(sid)               # back-pressure: RAM không tăng theo file
conn.send(sid, pack({"t": "FILE_END", "sha256": digest}), fin=True)
await self._announce_file(meta)                 # FILE_LOG -> FILE_OK (thẻ file trong lịch sử)

# sau này, khi PEERS báo có người online: đẩy những file còn chờ
for user in self._online_targets(meta["to"]):
    if user in meta["delivered"]:
        continue
    await self._p2p_push(user, meta, item)
    meta["delivered"].add(user)''',
         ["Khoá của peer lấy từ PEERS và được đối chiếu fingerprint trước byte đầu tiên: máy giả mạo không thể nhận file.",
          "Kết nối P2P được cache theo (người dùng, fingerprint); khi người đó đăng xuất hoặc đổi khoá, PEERS mới làm cache bị bỏ.",
          "Trạng thái file cho UI: file_start → file_progress → file_sent / file_queued (chờ người offline) / lỗi. "
          "Bắt tay TCP ở phía client (<i>_tcp_handshake</i>) kiểm HELLO_ACK và udp_port trước khi gọi Endpoint.connect."]),
        ("5.12 client/gateway.py — HTTP gateway cục bộ",
         "HTTP/1.1 server tối giản trên asyncio TCP: UI tĩnh, API JSON, SSE và upload/download dạng stream.",
         r'''if not self._host_ok(headers.get("host", "")):
    raise HttpError(403, "bad Host header")            # chặn DNS rebinding
if method == "POST" and headers.get("x-requested-with") != "collabnet":
    raise HttpError(403, "missing X-Requested-With")   # chặn form gửi từ trang lạ
...
fid = headers.get("x-file-id") or None
if fid is not None and not FILE_ID_RE.match(fid):
    raise HttpError(400, "invalid X-File-Id")         # fid làm tên file trong outbox
async def body():
    remaining = size
    while remaining > 0:
        data = await reader.read(min(65536, remaining))
        if not data:
            raise ConnectionError("upload interrupted")
        remaining -= len(data)
        yield data
fid = await self.core.send_file(to, name, size, body(), fid)''',
         ["Host phải là loopback (chống DNS rebinding) và POST phải có header riêng (form của trang khác không gắn được → chống CSRF); "
          "trang có Content-Security-Policy.",
          "Upload đọc 64 KB → yield → core gửi → drain(): không bước nào giữ cả file trong RAM.",
          "Tải về <i>?inline=1</i> (xem trước ảnh) kèm CSP sandbox; mặc định là attachment. Lỗi trả JSON {ok: false, error}."]),
        ("5.13 client/web/app.js — UI vẽ theo sự kiện",
         "JavaScript thuần, một kết nối SSE; tải lại trang là khôi phục trạng thái từ /api/state.",
         r'''function connectEvents() {
  const es = new EventSource("/api/events");
  const on = (name, fn) => es.addEventListener(name, (e) => fn(JSON.parse(e.data)));
  on("msg", (m) => { const r = addItem({ type: "msg", ...m }); ... });
  /* Lịch sử cũ do server gửi lại: thêm vào hội thoại nhưng không báo "chưa đọc". */
  on("history", (d) => { for (const m of d.items || []) addItem({ type: "msg", ...m }); });
  on("file_progress", (d) => { ... cập nhật thanh tiến trình ... });
  on("file_queued", (d) => { ... "đang chờ người nhận online" ... });
}''',
         ["Mọi sự kiện (status, peers, msg, history, sent, file_start / progress / sent / queued / received, stats, error) đi qua "
          "cùng một hàm on() nên chỉ cần một kết nối SSE cho toàn bộ giao diện.",
          "Gateway gửi dòng \": keep-alive\" mỗi 15 s để phát hiện tab đã đóng."]),
    ]
    for title, intro, src, notes in walk:
        S.append(KeepTogether([P(title, S_H3), P(intro), Spacer(1, 3),
                               code(src, title.split(" — ")[0].split(" ", 1)[1]), Spacer(1, 3)]))
        S += bullets(notes) + [Spacer(1, 6)]

    S += [P("5.14 Bộ kiểm thử", S_H3),
          P(f"{N_TESTS} kiểm thử chia theo lớp, chạy bằng <i>python -m unittest discover -s tests -t .</i> trong thư mục source/ "
            "(vài phút, vì có các kịch bản mất gói thật):"),
          Spacer(1, 3)]
    S.append(table([["File", "Nội dung kiểm tra"],
                    ["test_transport.py", "RangeSet, mã hoá/giải mã frame, crypto; 4 MB link sạch; 5% mất gói + đảo thứ tự (CUBIC, BBR); "
                     "flow control; không HoL; từ chối server sai khoá; phát hiện ngắt kết nối"],
                    ["test_e2e.py", "3 client thật trên loopback: đăng nhập, presence, broadcast/unicast, file P2P, đăng nhập trùng, "
                     "tự kết nối lại; chạy lại toàn bộ trên link 4% mất gói + 15 ms (BBR)"],
                    ["test_features.py", "Trạng thái gửi, thẻ file + giới hạn kích thước, lịch sử sau logout, tài khoản mới không thấy tin cũ, "
                     "file nhóm + tin/file cho người offline, upload bị ngắt"],
                    ["test_gateway.py", "HTTP thô: UI, đăng nhập, chat, upload/download, SSE, xem trước ảnh inline, font, chặn path traversal, "
                     "tin quá dài → 413"],
                    ["test_tcp_handshake.py", "HELLO → HELLO_ACK; sai phiên bản / rác không làm sập server; nhiều bắt tay đồng thời; "
                     "đăng nhập luôn bắt tay TCP trước; không có TCP → lỗi rõ ràng"],
                    ["test_regressions.py", "Lỗi đã sửa B1–B3, P1, P2, M1, D1–D3, G1 (đóng nhầm kết nối người gửi, AUTH chồng nhau, kẹt "
                     "reconnecting, ghi nguyên tử, Content-Length sai…) + so sánh tối ưu với cách tính vét cạn"],
                    ["test_review_fixes.py", "P2P đứt giữa chừng dọn file .part; file nhóm vẫn tới người khác khi peer đầu không với tới; "
                     "chặn file-id xấu; mẫu tốc độ BBR; discovery trên Python 3.10"]],
                   [3.7 * cm, 13.3 * cm], bold_first=True))

    # ---------------- 6. Giao diện, kiểm thử, hiệu năng
    S += [PageBreak()] + H1("6. Giao diện, kiểm thử và hiệu năng")
    S += [P("6.1 Giao diện web", S_H2),
          P("Giao diện hiển thị hội thoại chung và riêng, danh sách người online (kèm IP:port), thẻ file có thanh tiến trình gửi/nhận "
            "và chỉ số mạng thời gian thực (thuật toán CC, RTT, cwnd, số gói mất). Trình duyệt chỉ nói chuyện với gateway cục bộ:"),
          Spacer(1, 4),
          img("ui_screenshot.png", 16, "Hình 6. Giao diện CollabNet trong trình duyệt."),
          Spacer(1, 6)]
    S.append(table([["Endpoint", "Mô tả"],
                    ["GET /api/state", "Ảnh chụp trạng thái (người dùng, peers, tin, file) để dựng lại UI khi tải lại trang"],
                    ["GET /api/events", "SSE: status, peers, msg, history, sent, file_*, stats, error, notice"],
                    ["GET /api/discover", "Dò beacon server trong LAN (≈ 2 s)"],
                    ["POST /api/login · /api/logout", "Đăng nhập (TCP HELLO → UDP → AUTH) / đăng xuất; lỗi mạng → 502, sai mật khẩu → 401"],
                    ["POST /api/send", "Gửi tin {to, text}; rỗng → 400, quá 8192 ký tự → 413"],
                    ["POST /api/upload", "Thân là file thô; X-To, X-Filename, X-File-Id; đọc dạng stream 64 KB"],
                    ["GET /api/download/&lt;tên&gt;", "Tải file đã nhận (attachment), <i>?inline=1</i> để xem trước ảnh"]],
                   [4.6 * cm, 12.4 * cm], bold_first=True))
    S += [P("6.2 Kết quả kiểm thử", S_H2)]
    S.append(table([["Nhóm", "Nội dung kiểm tra", "KQ"],
                    ["Unit", "RangeSet, frame, crypto (ECDH, AES-GCM chống sửa header, PBKDF2), tên file Windows, ghi nguyên tử", "Đạt"],
                    ["Transport", "4 MB sạch; 5% mất gói + đảo thứ tự với CUBIC và BBR — SHA-256 khớp; flow control chặn đúng cửa sổ; "
                     "từ chối server sai khoá; phát hiện ngắt kết nối", "Đạt"],
                    ["Không HoL", "Tin chat nhỏ trong lúc file 3 MB đang truyền với 3% mất gói: độ trễ khoảng 20–30 ms/tin", "Đạt"],
                    ["E2E 3 client", "Presence, broadcast, unicast không rò rỉ, file P2P + file rỗng, client biến mất đột ngột, đăng nhập trùng, "
                     "tự kết nối lại, lịch sử sau logout, tin và file cho người offline; lặp lại trên link 4% mất gói + 15 ms", "Đạt"],
                    ["Gateway", "Tĩnh / API / SSE, upload stream, tải về, thiếu X-Requested-With, Host lạ, path traversal, Content-Length xấu", "Đạt"],
                    ["Bắt tay TCP", "HELLO/ACK, sai phiên bản, dữ liệu rác, nhiều kết nối đồng thời, không có listener TCP", "Đạt"]],
                   [2.7 * cm, 12.8 * cm, 1.5 * cm], bold_first=True))
    S += [P("6.3 Hiệu năng: CUBIC so với BBR", S_H2),
          P("Truyền 2 MB qua link mô phỏng RTT 20 ms với tỉ lệ mất gói khác nhau (<i>docs/benchmark.py</i>, kết quả trong benchmark.json):"),
          img("bench.png", 13.5, "Hình 7. Thông lượng theo tỉ lệ mất gói."),
          Spacer(1, 4)]
    rows = [["Mất gói", "CUBIC (Mbps)", "BBR (Mbps)", "Gói mất CUBIC / BBR"]]
    for l in sorted({r["loss"] for r in bench}):
        c = next(r for r in bench if r["loss"] == l and r["cc"] == "cubic")
        b = next(r for r in bench if r["loss"] == l and r["cc"] == "bbr")
        rows.append([f"{l * 100:.0f}%", f"{c['mbps']:.2f}", f"{b['mbps']:.2f}", f"{c['lost']} / {b['lost']}"])
    S += [table(rows, [3 * cm, 3.6 * cm, 3.6 * cm, 4.2 * cm]), Spacer(1, 5),
          P("Khi không mất gói, CUBIC nhỉnh hơn (slow start tích cực). Khi mất 1–5% gói, CUBIC nhân cửa sổ với 0.7 ở mỗi lần mất nên "
            "thông lượng sụp còn khoảng 2–6 Mbps, trong khi BBR dựa trên mô hình băng thông × RTT nên vẫn giữ 27–37 Mbps — đúng với "
            "phân tích loss-based và model-based. Đây là lý do chương trình cho chọn thuật toán bằng tham số <i>--cc</i>.")]

    # ---------------- 7. Thách thức
    S += [PageBreak()] + H1("7. Thách thức và cách giải quyết")
    ch = [
        ("Head-of-line blocking khi chat cùng file lớn",
         "Transport đa stream: mỗi tin / mỗi file một stream, chat ưu tiên cao hơn file, xoay vòng giữa các file. Đo được độ trễ chat "
         "khoảng 20–30 ms dù file đang truyền với 3% mất gói."),
        ("Đề yêu cầu TCP handshake nhưng giao thức chạy trên UDP",
         "Thêm bước bắt tay TCP thật (HELLO → HELLO_ACK) cùng số cổng: client xác nhận server sống, đúng phiên bản và biết cổng UDP "
         "trước khi chuyển sang UDP. TCP chỉ dùng cho bước này nên không mất ưu điểm không bị HoL."),
        ("Mơ hồ khi đo RTT / phân biệt gửi lại",
         "Packet number mới cho mọi lần gửi (kiểu QUIC) và ghi nhớ frame nào nằm trong gói nào; khi gói mất chỉ đưa lại <i>dải byte</i> "
         "tương ứng vào hàng đợi gửi lại."),
        ("Phân mảnh IP",
         "Datagram luôn ≤ 1200 B và tự chia dữ liệu thành frame STREAM, tránh phân mảnh IP — mất một mảnh là mất cả gói."),
        ("Áp lực ngược khi gửi file",
         "Gateway đọc 64 KB rồi <i>await drain()</i>. Lỗi thật gặp: hai tác vụ cùng chờ drain trên một stream thì callback sau ghi đè "
         "callback trước, luồng gửi đứng vĩnh viễn khi link mất gói. Sửa bằng danh sách callback + đánh thức tất cả khi stream/kết nối đóng."),
        ("Gửi file mà server không được thấy nội dung",
         "P2P trực tiếp: server chỉ công bố ip/port + fingerprint Ed25519; bên gửi đối chiếu fingerprint trước byte đầu. Server chỉ nhận "
         "FILE_LOG (tên, kích thước, sha256) để hiện thẻ file trong lịch sử."),
        ("Người nhận đang offline",
         "Tin nhắn: server vẫn lưu khi người nhận có tài khoản, trả SENT n = 0 và gửi lại trong HISTORY. File: bên gửi giữ trong outbox "
         "(ghi nguyên tử index.json) và tự đẩy khi PEERS báo người nhận online; chat nhóm theo dõi ai đã nhận."),
        ("Mất kết nối bất ngờ / NAT",
         "PING 4 s, idle timeout 20 s; server gỡ user và phát PEERS mới; client tự kết nối lại với backoff 1 → 15 s và đăng nhập lại; "
         "gói hợp lệ từ địa chỉ mới cập nhật địa chỉ peer; đăng nhập trùng đá phiên cũ."),
        ("Bảo mật trên UDP",
         "Không có TLS sẵn: ghép các primitive chuẩn (X25519 + HKDF + AES-GCM), ký bắt tay bằng Ed25519 chống MITM, ghim khoá kiểu SSH, "
         "nonce không lặp nhờ packet number đơn điệu, cửa sổ chống replay, giới hạn số stream / credit để tránh cạn bộ nhớ."),
        ("Trình duyệt không nói UDP, và đề cấm framework",
         "HTTP server tối giản trên asyncio TCP (parser + SSE + upload stream); chặn CSRF / DNS rebinding bằng header riêng + kiểm tra Host, "
         "thêm Content-Security-Policy."),
    ]
    S.append(table([["Thách thức", "Giải pháp"]] + [[a, b] for a, b in ch], [4.3 * cm, 12.7 * cm], bold_first=True))
    S += [P("Hạn chế đã biết", S_H2)] + bullets([
        "Chưa chống khuếch đại / giả mạo địa chỉ ở INITIAL (cần cookie / Retry như QUIC); BBR là bản rút gọn v1; chỉ hỗ trợ IPv4.",
        "File P2P chỉ chạy khi hai client kết nối trực tiếp được (không có relay/TURN cho NAT đối xứng); cần mở 9000/TCP, 9000/UDP và "
        "cổng P2P ngẫu nhiên trên tường lửa.",
        "Giao file cho người offline cần <b>bên gửi</b> và người nhận cùng online lại vào một lúc nào đó, vì byte nằm ở outbox của bên gửi.",
        "Bên nhận P2P chưa xác thực bên gửi (trường <i>from</i> do bên gửi tự khai); bên gửi thì luôn xác thực bên nhận qua fingerprint.",
        "Lịch sử là một file JSON giới hạn 4000 mục; mỗi lần đăng nhập chỉ phát lại 300 mục / 512 KB.",
    ])

    # ---------------- Phụ lục B: chạy chương trình
    S += [CondPageBreak(9 * cm), P("Phụ lục. Hướng dẫn chạy chương trình", S_H1),
          HRFlowable(width="100%", thickness=1.6, color=colors.HexColor(ACCENT), spaceBefore=2, spaceAfter=8),
          code("cd source\n"
               "pip install -r requirements.txt                 # cryptography\n"
               "python -m server.server --port 9000 [--cc bbr] [--max-file-mb 512] [--sim-loss 0.03]\n"
               "python -m client.main --ui-port 8080 --server 127.0.0.1:9000 --open   # client 2: --ui-port 8081\n"
               "python -m server.reset --dry-run                # xem trước việc xoá tài khoản + lịch sử\n"
               "python -m unittest discover -s tests -t .       # bộ kiểm thử\n"
               "python docs/benchmark.py                        # đo CUBIC / BBR -> benchmark.json", "chạy trong thư mục source/"),
          Spacer(1, 5),
          P("Mở trình duyệt tại http://127.0.0.1:8080 (client thứ hai: 8081), nhập địa chỉ server dạng host:9000, tên đăng nhập "
            "và mật khẩu; tên chưa có sẽ được tự đăng ký. Trên mạng LAN cần mở 9000/TCP, 9000/UDP và cổng P2P trên tường lửa.")]

    doc = Doc(os.path.join(HERE, "report.pdf"))
    doc.multiBuild(S, canvasmaker=NumberedCanvas)
    print(f"report.pdf written ({N_TESTS} tests)")


if __name__ == "__main__":
    build()
