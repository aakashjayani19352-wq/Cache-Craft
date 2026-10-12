"""
build_report/styles.py — Typography, layout, borders, XML helpers, and document styling.
Strictly adheres to PPSU formatting: A4 paper, Cambria font, 1.5 line spacing, justified body,
1.25" left margin (for hard binding), 1.0" top/right margins, 0.75" bottom margin.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Color Palette
COLOR_PRIMARY = RGBColor(15, 23, 42)      # Slate 900
COLOR_SECONDARY = RGBColor(30, 41, 59)   # Slate 800
COLOR_MUTED = RGBColor(71, 85, 105)      # Slate 600
COLOR_BODY = RGBColor(30, 30, 30)        # Near Black
COLOR_WHITE = RGBColor(255, 255, 255)
HEX_HEADER_BG = "1E293B"                 # Dark Slate
HEX_ZEBRA_BG = "F8FAFC"                  # Very light gray/slate
HEX_BORDER = "CBD5E1"                    # Light border
HEX_CALLOUT_BG = "F1F5F9"                # Subtle callout box

def setup_document_styles(doc):
    """Configures global styles for the document."""
    # Base Normal Style
    normal = doc.styles['Normal']
    normal.font.name = 'Cambria'
    normal.font.size = Pt(12)
    normal.font.color.rgb = COLOR_BODY
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.space_before = Pt(0)

    # Heading 1
    h1 = doc.styles['Heading 1']
    h1.font.name = 'Cambria'
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = COLOR_PRIMARY
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    h1.paragraph_format.line_spacing = 1.15
    h1.paragraph_format.keep_with_next = True

    # Heading 2
    h2 = doc.styles['Heading 2']
    h2.font.name = 'Cambria'
    h2.font.size = Pt(13)
    h2.font.bold = True
    h2.font.color.rgb = COLOR_SECONDARY
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    h2.paragraph_format.line_spacing = 1.15
    h2.paragraph_format.keep_with_next = True

    # Heading 3
    h3 = doc.styles['Heading 3']
    h3.font.name = 'Cambria'
    h3.font.size = Pt(12)
    h3.font.bold = True
    h3.font.italic = True
    h3.font.color.rgb = COLOR_MUTED
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(2)
    h3.paragraph_format.line_spacing = 1.15
    h3.paragraph_format.keep_with_next = True

def set_cell_background(cell, fill_hex):
    """Sets the solid background shading color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=90, bottom=90, left=130, right=130):
    """Sets internal padding (in twips/dxa) for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color=HEX_BORDER, sz="4", val="single"):
    """Applies neat subtle borders around and inside a table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_table_header_repeat(row):
    """Ensures table header repeats on next page when table splits."""
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def make_row_cant_split(row):
    """Prevents table row from being split across page boundaries."""
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def add_h1(doc, text, page_break=True):
    """Adds a Heading 1 paragraph, starting on a fresh page by default."""
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph(text, style='Heading 1')
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(8)
    return p

def add_h2(doc, text):
    """Adds a Heading 2 paragraph."""
    p = doc.add_paragraph(text, style='Heading 2')
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    return p

def add_h3(doc, text):
    """Adds a Heading 3 paragraph."""
    p = doc.add_paragraph(text, style='Heading 3')
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    return p

def add_p(doc, text, bold_prefix="", italic_prefix="", space_after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Adds a standard body paragraph with Cambria 12pt, 1.5 line spacing, and optional prefix."""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)

    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = 'Cambria'
        r_pre.font.size = Pt(12)
    if italic_prefix:
        r_pre2 = p.add_run(italic_prefix)
        r_pre2.italic = True
        r_pre2.font.name = 'Cambria'
        r_pre2.font.size = Pt(12)

    r = p.add_run(text)
    r.font.name = 'Cambria'
    r.font.size = Pt(12)
    return p

def add_bullet(doc, text, bold_prefix="", space_after=3):
    """Adds an indented bullet point with clean typography."""
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(space_after)

    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = 'Cambria'
        r_pre.font.size = Pt(11.5)
    r = p.add_run(text)
    r.font.name = 'Cambria'
    r.font.size = Pt(11.5)
    return p

def add_styled_table(doc, headers, data, col_widths=None, alignments=None, caption=None):
    """
    Renders an academic-grade table with dark header, alternating zebra stripes,
    explicit column widths, and proper cell paddings.
    """
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cap.paragraph_format.space_before = Pt(10)
        p_cap.paragraph_format.space_after = Pt(4)
        p_cap.paragraph_format.keep_with_next = True
        r_cap = p_cap.add_run(caption)
        r_cap.bold = True
        r_cap.font.name = 'Cambria'
        r_cap.font.size = Pt(11)
        r_cap.font.color.rgb = COLOR_PRIMARY

    num_rows = len(data) + 1
    num_cols = len(headers)
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    # Format Header Row
    header_row = table.rows[0]
    make_table_header_repeat(header_row)
    make_row_cant_split(header_row)
    for c_idx, cell in enumerate(header_row.cells):
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        align = alignments[c_idx] if alignments and c_idx < len(alignments) else WD_ALIGN_PARAGRAPH.LEFT
        p.alignment = align
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(headers[c_idx])
        run.bold = True
        run.font.name = 'Cambria'
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_WHITE

    # Format Data Rows
    for r_idx, row_data in enumerate(data):
        row = table.rows[r_idx + 1]
        make_row_cant_split(row)
        bg = HEX_ZEBRA_BG if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            align = alignments[c_idx] if alignments and c_idx < len(alignments) else WD_ALIGN_PARAGRAPH.LEFT
            p.alignment = align
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            val = str(row_data[c_idx]) if c_idx < len(row_data) else ""
            run = p.add_run(val)
            run.font.name = 'Cambria'
            run.font.size = Pt(9.5)
            run.font.color.rgb = COLOR_BODY

    # Set Column Widths if provided
    if col_widths:
        for row in table.rows:
            for c_idx, w in enumerate(col_widths):
                if c_idx < len(row.cells):
                    row.cells[c_idx].width = Inches(w)

    # Space after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(2)
    p_after.paragraph_format.space_after = Pt(8)
    return table

def add_figure(doc, img_path, fig_num_str, caption_text, width_inches=5.8):
    """
    Embeds a high-resolution image centered with standard university caption underneath.
    """
    if not os.path.exists(img_path):
        print(f"Warning: Figure image path not found: {img_path}")
        return

    # Image paragraph
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(12)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_inches))

    # Caption paragraph
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(12)
    
    r_lbl = p_cap.add_run(f"Figure {fig_num_str}: ")
    r_lbl.bold = True
    r_lbl.font.name = 'Cambria'
    r_lbl.font.size = Pt(10.5)
    r_lbl.font.color.rgb = COLOR_PRIMARY

    r_txt = p_cap.add_run(caption_text)
    r_txt.italic = True
    r_txt.font.name = 'Cambria'
    r_txt.font.size = Pt(10.5)
    r_txt.font.color.rgb = COLOR_SECONDARY

def add_callout(doc, text, title="KEY ARCHITECTURAL HIGHLIGHT"):
    """Adds a clean shaded callout box with a subtle border for emphasis."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, HEX_CALLOUT_BG)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_HEADER_BG}"/>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.25

    if title:
        r_t = p.add_run(f"{title}: ")
        r_t.bold = True
        r_t.font.name = 'Cambria'
        r_t.font.size = Pt(10.5)
        r_t.font.color.rgb = COLOR_PRIMARY

    r = p.add_run(text)
    r.italic = True
    r.font.name = 'Cambria'
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_BODY

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(6)

def add_code_snippet(doc, code_str):
    """Formats an excerpt of code or DDL schema with monospace font and gray background."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    set_table_borders(tbl, color="CBD5E1", sz="4", val="single")

    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05

    r = p.add_run(code_str)
    r.font.name = 'Consolas'
    r.font.size = Pt(9.0)
    r.font.color.rgb = COLOR_SECONDARY

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(6)
