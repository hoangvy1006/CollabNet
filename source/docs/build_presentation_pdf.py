"""Sinh docs/presentation_script.pdf từ docs/presentation_script.md.

Chạy trong thư mục source/:
    python docs/build_presentation_pdf.py

Không cần thư viện Markdown: tài liệu chỉ dùng một tập con Markdown cố định
(heading, đoạn văn, bullet, số thứ tự, blockquote, bảng, code fence, đường kẻ).
"""
from __future__ import annotations

import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "presentation_script.md")
OUTPUT = os.path.join(HERE, "presentation_script.pdf")

PAGE_W, PAGE_H = A4
MARGIN_X = 1.8 * cm
MARGIN_TOP = 1.9 * cm
MARGIN_BOTTOM = 1.7 * cm
CONTENT_W = PAGE_W - 2 * MARGIN_X


def _first(paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return paths[0]


FD = "/usr/share/fonts/truetype/dejavu/"
WIN = "C:/Windows/Fonts/"
REG = _first([FD + "DejaVuSans.ttf", WIN + "segoeui.ttf", WIN + "arial.ttf"])
BOLD = _first([FD + "DejaVuSans-Bold.ttf", WIN + "segoeuib.ttf", WIN + "arialbd.ttf"])
MONO = _first([FD + "DejaVuSansMono.ttf", WIN + "consola.ttf", WIN + "cour.ttf"])
pdfmetrics.registerFont(TTFont("DV", REG))
pdfmetrics.registerFont(TTFont("DV-B", BOLD))
pdfmetrics.registerFont(TTFont("DVM", MONO))

INK = colors.HexColor("#1b2430")
BLUE = colors.HexColor("#123a63")
BLUE2 = colors.HexColor("#1f4e79")
BLUE3 = colors.HexColor("#2f5d8a")
GREY = colors.HexColor("#657286")
LINE = colors.HexColor("#c9d4e0")
CODE_BG = colors.HexColor("#f6f8fa")
QUOTE_BG = colors.HexColor("#eef4ff")
QUOTE_LINE = colors.HexColor("#9bbcf2")
TABLE_HEAD = colors.HexColor("#e8eef7")


def styles():
    sheet = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle("CoverTitle", fontName="DV-B", fontSize=25, leading=31,
                                      textColor=BLUE, spaceAfter=8),
        "cover_meta": ParagraphStyle("CoverMeta", fontName="DV", fontSize=10.5, leading=15,
                                     textColor=INK, spaceAfter=2),
        "cover_sub": ParagraphStyle("CoverSub", fontName="DV", fontSize=10, leading=14,
                                    textColor=GREY),
        "h1": ParagraphStyle("H1", fontName="DV-B", fontSize=15.5, leading=19, textColor=BLUE,
                             spaceBefore=4, spaceAfter=8, keepWithNext=1),
        "h2": ParagraphStyle("H2", fontName="DV-B", fontSize=12.2, leading=15.5, textColor=BLUE2,
                             spaceBefore=10, spaceAfter=4, keepWithNext=1),
        "h3": ParagraphStyle("H3", fontName="DV-B", fontSize=10.6, leading=13.5, textColor=BLUE3,
                             spaceBefore=8, spaceAfter=3, keepWithNext=1),
        "body": ParagraphStyle("Body", fontName="DV", fontSize=9.6, leading=13.7, textColor=INK,
                               spaceAfter=5, alignment=TA_LEFT),
        "quote": ParagraphStyle("Quote", fontName="DV", fontSize=9.6, leading=13.7, textColor=INK,
                                leftIndent=10, rightIndent=4, spaceBefore=3, spaceAfter=7,
                                backColor=QUOTE_BG, borderColor=QUOTE_LINE, borderWidth=0.6,
                                borderPadding=6),
        "bullet": ParagraphStyle("Bullet", fontName="DV", fontSize=9.6, leading=13.5, textColor=INK,
                                 leftIndent=16, bulletIndent=3, spaceAfter=2),
        "num": ParagraphStyle("Num", fontName="DV", fontSize=9.6, leading=13.5, textColor=INK,
                              leftIndent=18, firstLineIndent=-13, spaceAfter=2),
        "code": ParagraphStyle("Code", fontName="DVM", fontSize=7.1, leading=8.8, textColor=INK,
                               backColor=CODE_BG, borderColor=colors.HexColor("#dde3ea"),
                               borderWidth=0.4, borderPadding=5, leftIndent=6, spaceBefore=3,
                               spaceAfter=7),
        "table_cell": ParagraphStyle("TableCell", fontName="DV", fontSize=7.1, leading=8.9,
                                     textColor=INK, alignment=TA_LEFT),
        "table_head": ParagraphStyle("TableHead", fontName="DV-B", fontSize=7.1, leading=8.9,
                                     textColor=BLUE, alignment=TA_LEFT),
        "toc_title": ParagraphStyle("TocTitle", fontName="DV-B", fontSize=15.5, leading=19,
                                    textColor=BLUE, spaceAfter=10),
        "toc0": ParagraphStyle("TOC0", fontName="DV-B", fontSize=9.4, leading=13,
                               textColor=BLUE, spaceBefore=3, rightIndent=22),
        "toc1": ParagraphStyle("TOC1", fontName="DV", fontSize=8.5, leading=11.2,
                               textColor=INK, leftIndent=14, rightIndent=22),
        "caption": ParagraphStyle("Caption", fontName="DV", fontSize=8, leading=10,
                                  textColor=GREY, spaceAfter=4),
    }


ST = styles()


def inline(text: str, code_size: str = "8.3") -> str:
    """Chuyển **đậm**, `code` và escape XML cho Paragraph."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", rf'<font name="DVM" size="{code_size}">\1</font>', text)
    return text


def split_table_row(row: str) -> list[str]:
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", row)]


def is_separator(row: str) -> bool:
    return bool(re.match(r"^\|[\s:\-|]+\|$", row.strip())) and "-" in row


def wrap_code(text: str, width: int = 112) -> str:
    """Bẻ dòng code quá dài để không tràn trang; giữ thụt lề tương đối."""
    out = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if len(line) <= width:
            out.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        prefix = " " * indent
        rest = line
        while len(rest) > width:
            cut = rest.rfind(" ", 0, width)
            if cut <= indent + 6:
                cut = width
            out.append(rest[:cut].rstrip())
            rest = prefix + "    " + rest[cut:].lstrip()
        out.append(rest)
    return "\n".join(out)


def parse(md: str):
    """Trả về (title, cover_meta, blocks)."""
    lines = md.splitlines()
    title, cover_meta, blocks = "KỊCH BẢN THUYẾT TRÌNH", [], []
    i = 0
    seen_h1 = False
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(buf)))
            continue
        if s.startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            rows = [lines[i].strip()]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            blocks.append(("table", rows))
            continue
        if s.startswith("# ") and not blocks and not cover_meta:
            title = s[2:].strip()
            i += 1
            continue
        if s.startswith("## "):
            seen_h1 = True
            blocks.append(("h1", s[3:].strip()))
            i += 1
            continue
        if s.startswith("### "):
            blocks.append(("h2", s[4:].strip()))
            i += 1
            continue
        if s.startswith("#### "):
            blocks.append(("h3", s[5:].strip()))
            i += 1
            continue
        if s == "---":
            blocks.append(("hr", None))
            i += 1
            continue
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append(("quote", " ".join(x for x in buf if x)))
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            buf = [s]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    break
                t = nxt.strip()
                if re.match(r"^\d+\.\s", t) or t.startswith(("```", "|", "#", ">", "- ")) or t == "---":
                    break
                if nxt.startswith(("   ", "\t")):
                    buf.append(t)
                    i += 1
                else:
                    break
            blocks.append(("num", " ".join(buf)))
            continue
        if s.startswith("- "):
            buf = [s[2:]]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    break
                t = nxt.strip()
                if t.startswith(("```", "|", "#", ">", "- ")) or t == "---" or re.match(r"^\d+\.\s", t):
                    break
                if nxt.startswith(("  ", "\t")):
                    buf.append(t)
                    i += 1
                else:
                    break
            blocks.append(("bullet", " ".join(buf)))
            continue
        # paragraph
        buf = [s]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if not nxt.strip():
                break
            t = nxt.strip()
            if t.startswith(("#", "```", "|", ">", "- ")) or t == "---" or re.match(r"^\d+\.\s", t):
                break
            buf.append(t)
            i += 1
        text = " ".join(buf)
        if not seen_h1 and not blocks:
            cover_meta.append(text)
        else:
            blocks.append(("p", text))
    return title, cover_meta, blocks


def make_table(rows: list[str], width: float) -> Table:
    data = [split_table_row(r) for r in rows]
    ncols = max(len(r) for r in data)
    for row in data:
        row += [""] * (ncols - len(row))

    # Độ rộng cột theo độ dài trung bình, có sàn để không bóp chữ.
    weights = []
    for c in range(ncols):
        vals = [len(re.sub(r"[`*]", "", row[c])) for row in data[1:]] or [10]
        weights.append(max(6, min(42, sum(vals) / len(vals))))
    total = sum(weights)
    widths = [width * w / total for w in weights]
    floor = 44
    for _ in range(6):
        deficit = sum(max(0, floor - w) for w in widths)
        if deficit <= 0:
            break
        surplus = sum(max(0, w - floor) for w in widths)
        if surplus <= 0:
            break
        widths = [max(floor, w - (max(0, w - floor) / surplus) * deficit) for w in widths]
    scale = width / sum(widths)
    widths = [w * scale for w in widths]

    body = []
    for r, row in enumerate(data):
        style = ST["table_head"] if r == 0 else ST["table_cell"]
        body.append([Paragraph(inline(cell, "6.7") if cell else "", style) for cell in row])

    table = Table(body, colWidths=widths, repeatRows=1, splitByRow=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c7d2df")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return table


class Doc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="main")
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self._decorate)])

    def _decorate(self, canvas, doc):
        if doc.page == 1:
            return
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN_X, PAGE_H - MARGIN_TOP + 16, PAGE_W - MARGIN_X, PAGE_H - MARGIN_TOP + 16)
        canvas.setFont("DV", 7.8)
        canvas.setFillColor(GREY)
        canvas.drawString(MARGIN_X, PAGE_H - MARGIN_TOP + 21,
                          "CollabNet — Kịch bản thuyết trình & demo")
        canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - MARGIN_TOP + 21, f"{doc.page}")
        canvas.line(MARGIN_X, MARGIN_BOTTOM - 14, PAGE_W - MARGIN_X, MARGIN_BOTTOM - 14)
        canvas.drawString(MARGIN_X, MARGIN_BOTTOM - 25,
                          "Assignment 1 — Network Application Development")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        name = flowable.style.name
        if name == "H1":
            self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))
        elif name == "H2":
            self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))


def build():
    with open(SOURCE, encoding="utf-8") as fh:
        md = fh.read()
    title, cover_meta, blocks = parse(md)

    story = [Spacer(1, 80), Paragraph(inline(title), ST["cover_title"]), Spacer(1, 4),
             HRFlowable(width="100%", thickness=2, color=BLUE, spaceBefore=2, spaceAfter=14)]
    for meta in cover_meta[:4]:
        story.append(Paragraph(inline(meta, "9.5"), ST["cover_meta"]))
    story += [Spacer(1, 26),
              Paragraph("Tài liệu dùng để thuyết trình và thao tác Wireshark trực tiếp trước giảng viên.",
                        ST["cover_sub"]),
              Spacer(1, 6),
              Paragraph("10 bước tương ứng 10 tiêu chí chấm điểm — mỗi bước có lời nói, demo web và filter Wireshark.",
                        ST["cover_sub"]),
              PageBreak()]

    toc = TableOfContents()
    toc.levelStyles = [ST["toc0"], ST["toc1"]]
    toc.dotsMinLevel = 0
    story += [Paragraph("MỤC LỤC", ST["toc_title"]), toc, PageBreak()]

    first_h1 = True
    for kind, value in blocks:
        if kind == "h1":
            if not first_h1:
                story.append(PageBreak())
            first_h1 = False
            story.append(Paragraph(inline(value), ST["h1"]))
        elif kind == "h2":
            story.append(Paragraph(inline(value), ST["h2"]))
        elif kind == "h3":
            story.append(Paragraph(inline(value), ST["h3"]))
        elif kind == "p":
            story.append(Paragraph(inline(value), ST["body"]))
        elif kind == "quote":
            story.append(Paragraph(inline(value), ST["quote"]))
        elif kind == "bullet":
            story.append(Paragraph(inline(value), ST["bullet"], bulletText="•"))
        elif kind == "num":
            story.append(Paragraph(inline(value), ST["num"]))
        elif kind == "code":
            story.append(Preformatted(wrap_code(value), ST["code"]))
        elif kind == "table":
            story.append(make_table(value, CONTENT_W))
            story.append(Spacer(1, 7))
        elif kind == "hr":
            story.append(Spacer(1, 3))
            story.append(HRFlowable(width="100%", thickness=0.7, color=LINE, spaceBefore=2, spaceAfter=6))

    doc = Doc(OUTPUT, pagesize=A4, leftMargin=MARGIN_X, rightMargin=MARGIN_X,
              topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
              title="CollabNet — Kịch bản thuyết trình & demo",
              author="CollabNet", subject="Assignment 1 — Network Application Development")
    doc.multiBuild(story)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    build()
