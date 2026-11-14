# -*- coding: utf-8 -*-
"""Мини-генератор DOCX: стили, код, таблицы, колонтитулы, мини-markdown."""
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ACCENT = RGBColor(0x1F, 0x38, 0x64)
ACCENT2 = RGBColor(0x2E, 0x54, 0x96)
MUTED = RGBColor(0x5A, 0x63, 0x70)
CODE_BG = "F3F5F8"
BORDER = "D5DBE3"
BODY_FONT = "Calibri"
MONO_FONT = "Consolas"


# ---------------------------------------------------------------- низкий уровень
def _el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k), str(v))
    return e


def _shd(el_parent, fill):
    shd = _el("w:shd", **{"w:val": "clear", "w:color": "auto", "w:fill": fill})
    el_parent.append(shd)


def _borders(ppr, color=BORDER, sz=4, left=True, left_color=None, left_sz=None):
    pbdr = _el("w:pBdr")
    if left:
        pbdr.append(_el("w:left", **{"w:val": "single", "w:sz": str(left_sz or 18),
                                     "w:space": "6", "w:color": left_color or ACCENT2.__str__()}))
    pbdr.append(_el("w:top", **{"w:val": "single", "w:sz": str(sz), "w:space": "2", "w:color": color}))
    pbdr.append(_el("w:bottom", **{"w:val": "single", "w:sz": str(sz), "w:space": "2", "w:color": color}))
    pbdr.append(_el("w:right", **{"w:val": "single", "w:sz": str(sz), "w:space": "2", "w:color": color}))
    ppr.append(pbdr)


def _field(paragraph, code, text_color=None, size=None, bold=False):
    run = paragraph.add_run()
    run._r.append(_el("w:fldChar", **{"w:fldCharType": "begin"}))
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {code} "
    run._r.append(it)
    run._r.append(_el("w:fldChar", **{"w:fldCharType": "separate"}))
    t = OxmlElement("w:t")
    t.text = "1"
    run._r.append(t)
    run._r.append(_el("w:fldChar", **{"w:fldCharType": "end"}))
    run.font.size = Pt(size or 8)
    run.font.name = BODY_FONT
    if text_color is not None:
        run.font.color.rgb = text_color
    run.bold = bold
    return run


# ---------------------------------------------------------------- документ
def new_doc(header_text, doc_title, footer_text):
    doc = Document()

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(1.9)
    sec.left_margin, sec.right_margin = Cm(2.1), Cm(2.0)
    sec.header_distance, sec.footer_distance = Cm(0.9), Cm(0.8)

    st = doc.styles["Normal"]
    st.font.name = BODY_FONT
    st.font.size = Pt(10.5)
    st.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = _el("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), BODY_FONT)
    pf = st.paragraph_format
    pf.space_after = Pt(5)
    pf.space_before = Pt(0)
    pf.line_spacing = 1.16
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def heading(name, size, color, before, after, bold=True):
        s = doc.styles[name]
        s.font.name = BODY_FONT
        s.font.size = Pt(size)
        s.font.bold = bold
        s.font.color.rgb = color
        s.font.italic = False
        p = s.paragraph_format
        p.space_before = Pt(before)
        p.space_after = Pt(after)
        p.keep_with_next = True
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.line_spacing = 1.0
        # шрифт для кириллицы
        r = s.element.get_or_add_rPr()
        f = r.find(qn("w:rFonts"))
        if f is None:
            f = _el("w:rFonts")
            r.append(f)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            f.set(qn(a), BODY_FONT)

    heading("Heading 1", 20, ACCENT, 0, 10)
    heading("Heading 2", 14, ACCENT2, 14, 6)
    heading("Heading 3", 11.5, RGBColor(0x2B, 0x2B, 0x2B), 11, 4)

    for name in ("List Bullet",):
        s = doc.styles[name]
        s.font.name = BODY_FONT
        s.font.size = Pt(10.5)
        s.paragraph_format.space_after = Pt(2)
        s.paragraph_format.line_spacing = 1.12

    # ------ колонтитулы
    hp = sec.header.paragraphs[0]
    hp.text = ""
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    hr = hp.add_run(header_text)
    hr.font.size = Pt(8)
    hr.font.name = BODY_FONT
    hr.font.color.rgb = MUTED
    hp.paragraph_format.space_after = Pt(2)
    ppr = hp._p.get_or_add_pPr()
    pbdr = _el("w:pBdr")
    pbdr.append(_el("w:bottom", **{"w:val": "single", "w:sz": "6", "w:space": "4", "w:color": "C9D1DB"}))
    ppr.append(pbdr)

    fp = sec.footer.paragraphs[0]
    fp.text = ""
    fp.paragraph_format.space_before = Pt(2)
    fp.paragraph_format.tab_stops.add_tab_stop(Cm(16.9), WD_TAB_ALIGNMENT.RIGHT)
    r1 = fp.add_run(footer_text + "\t")
    r1.font.size = Pt(8)
    r1.font.name = BODY_FONT
    r1.font.color.rgb = MUTED
    r2 = fp.add_run("Стр. ")
    r2.font.size = Pt(8)
    r2.font.name = BODY_FONT
    r2.font.color.rgb = MUTED
    _field(fp, "PAGE", MUTED, 8)
    r3 = fp.add_run(" из ")
    r3.font.size = Pt(8)
    r3.font.name = BODY_FONT
    r3.font.color.rgb = MUTED
    _field(fp, "NUMPAGES", MUTED, 8)

    cp = doc.core_properties
    cp.title = doc_title
    cp.author = "Техническая документация проекта 3D_Model"
    cp.subject = "OpenGL 4.6 / C++ симуляция"
    cp.comments = "Сгенерировано автоматически по исходному коду проекта"
    return doc


# ---------------------------------------------------------------- rich text
TOKEN = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


def rich(par, text, size=None, color=None, italic=False):
    for part in TOKEN.split(text):
        if not part:
            continue
        bold = False
        mono = False
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            part, bold = part[2:-2], True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            part, mono = part[1:-1], True
        run = par.add_run(part)
        run.bold = bold
        run.font.name = MONO_FONT if mono else BODY_FONT
        run.font.size = Pt((size or 10.5) - (0.5 if mono else 0))
        if mono:
            run.font.color.rgb = RGBColor(0x8B, 0x1A, 0x3A)
        elif color is not None:
            run.font.color.rgb = color
        if italic:
            run.italic = True


# ---------------------------------------------------------------- блоки
def title_page(doc, kicker, title, subtitle, meta_rows, note=None):
    for _ in range(2):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(kicker.upper())
    r.font.size = Pt(9.5)
    r.font.bold = True
    r.font.color.rgb = ACCENT2
    r.font.name = BODY_FONT
    r.font.element.get_or_add_rPr().append(_el("w:spacing", **{"w:val": "40"}))

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 0.95
    r = p.add_run(title)
    r.font.size = Pt(34)
    r.font.bold = True
    r.font.color.rgb = ACCENT
    r.font.name = BODY_FONT

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(18)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(subtitle)
    r.font.size = Pt(13)
    r.font.color.rgb = MUTED
    r.font.name = BODY_FONT

    rule = doc.add_paragraph()
    rule.paragraph_format.space_after = Pt(16)
    ppr = rule._p.get_or_add_pPr()
    pbdr = _el("w:pBdr")
    pbdr.append(_el("w:bottom", **{"w:val": "single", "w:sz": "18", "w:space": "1", "w:color": "1F3864"}))
    ppr.append(pbdr)

    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for k, v in meta_rows:
        row = t.add_row().cells
        row[0].width = Cm(4.6)
        row[1].width = Cm(11.8)
        pk = row[0].paragraphs[0]
        pk.paragraph_format.space_after = Pt(3)
        rk = pk.add_run(k)
        rk.font.size = Pt(9)
        rk.font.bold = True
        rk.font.color.rgb = MUTED
        rk.font.name = BODY_FONT
        pv = row[1].paragraphs[0]
        pv.paragraph_format.space_after = Pt(3)
        pv.alignment = WD_ALIGN_PARAGRAPH.LEFT
        rich(pv, v, size=9.5)

    if note:
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        rich(p, note, size=9, color=MUTED, italic=True)


def h1(doc, text, new_page=True):
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.page_break_before = new_page
    p.paragraph_format.space_before = Pt(0 if new_page else 22)
    p.add_run(text)
    ppr = p._p.get_or_add_pPr()
    pbdr = _el("w:pBdr")
    pbdr.append(_el("w:bottom", **{"w:val": "single", "w:sz": "8", "w:space": "4", "w:color": "B4C2D6"}))
    ppr.append(pbdr)
    return p


def h2(doc, text):
    p = doc.add_paragraph(style="Heading 2")
    p.add_run(text)
    return p


def h3(doc, text):
    p = doc.add_paragraph(style="Heading 3")
    p.add_run(text)
    return p


def para(doc, text, **kw):
    p = doc.add_paragraph()
    rich(p, text, **kw)
    return p


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    rich(p, text)
    return p


def code(doc, text, caption=None):
    text = text.strip("\n")
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4)
    pf.space_after = Pt(7)
    pf.line_spacing = 1.0
    pf.left_indent = Cm(0.25)
    pf.right_indent = Cm(0.1)
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    ppr = p._p.get_or_add_pPr()
    _shd(ppr, CODE_BG)
    _borders(ppr)
    lines = text.split("\n")
    pf.keep_with_next = True
    pf.keep_together = len(lines) <= 26
    for i, line in enumerate(lines):
        run = p.add_run(line)
        run.font.name = MONO_FONT
        run.font.size = Pt(8.2)
        run.font.color.rgb = RGBColor(0x1B, 0x1F, 0x24)
        if i < len(lines) - 1:
            run.add_break()
    if caption:
        cap(doc, caption)
    return p


def cap(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(9)
    rich(p, text, size=8.5, color=MUTED, italic=True)
    return p


def note(doc, title, text):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]
    cell.width = Cm(16.2)
    tcpr = cell._tc.get_or_add_tcPr()
    _shd(tcpr, "FFF6E5")
    borders = _el("w:tcBorders")
    borders.append(_el("w:left", **{"w:val": "single", "w:sz": "24", "w:space": "0", "w:color": "E08A1E"}))
    for side in ("top", "bottom", "right"):
        borders.append(_el("w:" + side, **{"w:val": "single", "w:sz": "4", "w:space": "0", "w:color": "F0D9B5"}))
    tcpr.append(borders)
    mar = _el("w:tcMar")
    for side, v in (("top", 110), ("bottom", 110), ("left", 160), ("right", 140)):
        mar.append(_el("w:" + side, **{"w:w": str(v), "w:type": "dxa"}))
    tcpr.append(mar)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(title + "  ")
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x8A, 0x4B, 0x00)
    r.font.name = BODY_FONT
    rich(p, text, size=9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def img(doc, path, width_cm=15.8, caption=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Cm(width_cm))
    if caption:
        c = doc.add_paragraph()
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_after = Pt(10)
        rich(c, caption, size=8.5, color=MUTED, italic=True)


def table(doc, rows, header=True, sizes=None, caption=None, font_size=8.7, col_widths=None):
    if sizes:
        font_size = sizes
    ncols = len(rows[0])
    t = doc.add_table(rows=0, cols=ncols)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    if col_widths:
        t.autofit = False
        tblpr = t._tbl.tblPr
        tblpr.append(_el("w:tblLayout", **{"w:type": "fixed"}))
        tblw = _el("w:tblW", **{"w:w": str(int(sum(col_widths) * 567)), "w:type": "dxa"})
        tblpr.append(tblw)
        for i, cw in enumerate(col_widths):
            t.columns[i].width = Cm(cw)
    else:
        t.autofit = True
    for ri, row in enumerate(rows):
        row = list(row[:ncols]) + [""] * max(0, ncols - len(row))
        cells = t.add_row().cells
        for ci, val in enumerate(row):
            cell = cells[ci]
            if col_widths:
                cell.width = Cm(col_widths[ci])
            tcpr = cell._tc.get_or_add_tcPr()
            mar = _el("w:tcMar")
            for side, v in (("top", 55), ("bottom", 55), ("left", 105), ("right", 105)):
                mar.append(_el("w:" + side, **{"w:w": str(v), "w:type": "dxa"}))
            tcpr.append(mar)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            txt = str(val)
            rich(p, txt, size=font_size)
            for run in p.runs:
                if ri == 0 and header:
                    run.bold = True
            if ri == 0 and header:
                _shd(tcpr, "DCE6F3")
        if ri == 0 and header:
            trpr = t.rows[0]._tr.get_or_add_trPr()
            trpr.append(_el("w:tblHeader", **{"w:val": "true"}))
        trpr = t.rows[-1]._tr.get_or_add_trPr()
        trpr.append(_el("w:cantSplit", **{"w:val": "true"}))
    if caption:
        c = doc.add_paragraph()
        c.paragraph_format.space_before = Pt(4)
        c.paragraph_format.space_after = Pt(10)
        rich(c, caption, size=8.5, color=MUTED, italic=True)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
    if len(rows) <= 9:
        for row in t.rows[:-1]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True
    return t


# ---------------------------------------------------------------- мини-markdown
def md(doc, text, caption=None):
    lines = text.strip("\n").split("\n")
    i = 0
    n = len(lines)
    pending_widths = None
    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue

        mw = re.match(r"^<!--\s*w:\s*([\d.,\s]+)\s*-->$", line.strip())
        if mw:
            pending_widths = [float(v) for v in mw.group(1).split(",")]
            i += 1
            continue

        if line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            code(doc, "\n".join(buf))
            continue

        if line.startswith("|"):
            rows = []

            def split_row(raw):
                raw = raw.strip()
                if raw.startswith("|"):
                    raw = raw[1:]
                if raw.endswith("|"):
                    raw = raw[:-1]
                cells, cur, in_bt = [], "", False
                for ch in raw:
                    if ch == "`":
                        in_bt = not in_bt
                        cur += ch
                    elif ch == "|" and not in_bt:
                        cells.append(cur.strip())
                        cur = ""
                    else:
                        cur += ch
                cells.append(cur.strip())
                return cells

            while i < n and lines[i].strip().startswith("|"):
                cells = split_row(lines[i])
                if not all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                table(doc, rows, col_widths=pending_widths)
            pending_widths = None
            continue

        if line.startswith("> "):
            buf = []
            while i < n and lines[i].startswith("> "):
                buf.append(lines[i][2:].strip())
                i += 1
            txt = " ".join(buf)
            if ":" in txt.split(".")[0] and len(txt.split(":", 1)[0]) < 40:
                head, body = txt.split(":", 1)
                note(doc, head.strip() + ":", body.strip())
            else:
                note(doc, "Важно.", txt)
            continue

        if line.startswith("- "):
            while i < n and lines[i].startswith("- "):
                bullet(doc, lines[i][2:].strip())
                i += 1
            continue

        m = re.match(r"^(\d+)\.\s+", line)
        if m:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.65)
            p.paragraph_format.first_line_indent = Cm(-0.65)
            p.paragraph_format.space_after = Pt(3)
            i += 1
            body = line
            while i < n and lines[i].strip() and not re.match(r"^(- |\d+\.\s|\||```|> |#{1,3} )", lines[i].strip()):
                body += " " + lines[i].strip()
                i += 1
            rich(p, body)
            continue

        if line.startswith("### "):
            h3(doc, line[4:].strip())
            i += 1
            continue
        if line.startswith("## "):
            h2(doc, line[3:].strip())
            i += 1
            continue

        # обычный абзац: склеиваем строки до пустой
        buf = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(- |\d+\.\s|\||```|> |#{1,3} )", lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        para(doc, " ".join(buf))

    if caption:
        cap(doc, caption)
