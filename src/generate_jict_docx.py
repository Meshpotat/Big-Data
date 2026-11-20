# -*- coding: utf-8 -*-
"""
Generate publication-ready Word document (.docx) strictly following
C:\\Users\\muham\\Downloads\\Template_Journal_JICT (1).docx (JICT / INISTA format).
"""

import os
import docx
from docx.shared import Pt, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

TEMPLATE_PATH = r"C:\Users\muham\Downloads\Template_Journal_JICT (1).docx"
OUTPUT_DOCX = r"c:\Bafqi\Big Data\Jurnal_JICT_INISTA_Kelompok_15.docx"
FIG_DIR = r"c:\Bafqi\Big Data\outputs\figures"

INDENT_EMU = 114300  # Exact first-line indent from template (0.125 inch / ~3.175 mm)


def set_cell_border(cell, **kwargs):
    """
    Set cell borders in a Word table (e.g., top, bottom, left, right).
    kwargs values: dict(sz=6, val='single', color='000000') or dict(val='nil')
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement("w:tcBorders")
        tcPr.append(tcBorders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f"w:{edge}"
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)
            for key in ["val", "color", "sz", "space"]:
                if key in edge_data:
                    element.set(qn(f"w:{key}"), str(edge_data[key]))


def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def format_run(
    run,
    size_pt=10,
    bold=False,
    italic=False,
    small_caps=False,
    superscript=False,
    font_name="Times New Roman",
):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.small_caps = small_caps
    run.font.superscript = superscript
    run.font.color.rgb = RGBColor(0, 0, 0)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"), font_name)


def add_level1_heading(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(text)
    format_run(r, size_pt=10, bold=False, italic=False, small_caps=True)
    return p


def add_level2_heading(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(text)
    format_run(r, size_pt=10, bold=False, italic=True, small_caps=False)
    return p


def add_level3_paragraph(doc, heading_prefix, body_text):
    """
    3) Level-3 Heading: indented, Italic, numbered with Arabic numeral followed by right parenthesis,
    ending with a colon. Body immediately follows in the same paragraph.
    """
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Emu(INDENT_EMU)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)
    r_head = p.add_run(heading_prefix + " ")
    format_run(r_head, size_pt=10, bold=False, italic=True)
    add_rich_runs(p, body_text, size_pt=10)
    return p


def add_rich_runs(p, text, size_pt=10, base_bold=False, base_italic=False):
    """
    Support inline *italic* segments in body text while keeping Times New Roman formatting.
    """
    parts = text.split("*")
    for idx, part in enumerate(parts):
        if not part:
            continue
        is_italic = base_italic or (idx % 2 == 1)
        r = p.add_run(part)
        format_run(r, size_pt=size_pt, bold=base_bold, italic=is_italic)


def add_body_paragraph(doc, text, drop_cap_first_word=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    if drop_cap_first_word:
        p.paragraph_format.first_line_indent = Pt(0)
        first_space = text.find(" ")
        first_word = text[:first_space]
        rest = text[first_space:]
        r_drop = p.add_run(first_word[0].upper())
        format_run(r_drop, size_pt=24, bold=True)
        r_caps = p.add_run(first_word[1:].upper())
        format_run(r_caps, size_pt=10, bold=False)
        add_rich_runs(p, rest, size_pt=10)
    else:
        p.paragraph_format.first_line_indent = Emu(INDENT_EMU)
        add_rich_runs(p, text, size_pt=10)
    return p


def add_equation_row(doc, lhs_rhs_text, eq_num_str):
    """
    Number equations consecutively with equation numbers in parentheses flush with the right margin.
    """
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(5.4)
    tbl.columns[1].width = Inches(0.7)

    c0 = tbl.cell(0, 0)
    c1 = tbl.cell(0, 1)
    for c in (c0, c1):
        set_cell_border(
            c,
            top={"val": "nil"},
            bottom={"val": "nil"},
            left={"val": "nil"},
            right={"val": "nil"},
        )
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.space_before = Pt(3)
    p0.paragraph_format.space_after = Pt(3)
    add_rich_runs(p0, lhs_rhs_text, size_pt=10, base_italic=True)

    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p1.paragraph_format.space_before = Pt(3)
    p1.paragraph_format.space_after = Pt(3)
    r_num = p1.add_run(eq_num_str)
    format_run(r_num, size_pt=10, bold=False, italic=False)


def add_inista_table(doc, roman_num, title_text, headers, rows, col_widths_in=None):
    """
    Tables must be numbered using uppercase Roman numerals.
    Table captions must be centered and in 8 pt regular font with Small Caps.
    Captions with table numbers must be placed before their associated tables.
    """
    p_num = doc.add_paragraph()
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_before = Pt(6)
    p_num.paragraph_format.space_after = Pt(0)
    p_num.paragraph_format.first_line_indent = Pt(0)
    r_num = p_num.add_run(f"TABLE {roman_num}")
    format_run(r_num, size_pt=8, bold=False, italic=False, small_caps=True)

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(3)
    p_cap.paragraph_format.first_line_indent = Pt(0)
    r_cap = p_cap.add_run(title_text)
    format_run(r_cap, size_pt=8, bold=False, italic=False, small_caps=True)

    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = True

    border_thin = {"sz": 6, "val": "single", "color": "000000"}
    border_thick = {"sz": 10, "val": "single", "color": "000000"}
    border_none = {"val": "nil"}

    # Header row
    for j, h_text in enumerate(headers):
        cell = tbl.cell(0, j)
        if col_widths_in and j < len(col_widths_in):
            cell.width = Inches(col_widths_in[j])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
        set_cell_border(
            cell,
            top=border_thick,
            bottom=border_thin,
            left=border_thin,
            right=border_thin,
        )
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.first_line_indent = Pt(0)
        r = p.add_run(h_text)
        format_run(r, size_pt=8.5, bold=True)

    # Data rows
    for i, row_vals in enumerate(rows):
        is_last = i == len(rows) - 1
        for j, val in enumerate(row_vals):
            cell = tbl.cell(i + 1, j)
            if col_widths_in and j < len(col_widths_in):
                cell.width = Inches(col_widths_in[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=40, bottom=40, left=70, right=70)
            set_cell_border(
                cell,
                top=border_thin,
                bottom=border_thick if is_last else border_thin,
                left=border_thin,
                right=border_thin,
            )
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.first_line_indent = Pt(0)
            val_str = str(val)
            is_bold = val_str.startswith("**") and val_str.endswith("**")
            if is_bold:
                val_str = val_str[2:-2]
            r = p.add_run(val_str)
            format_run(r, size_pt=8.5, bold=is_bold)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(2)


def add_inista_figure(doc, fig_num, img_path, caption_text, width_in=5.6):
    """
    Figures must be centered in the column.
    Figures must be numbered using Arabic numerals.
    Figure captions must be in 8 pt regular font.
    Captions with figure numbers must be placed after their associated figures.
    """
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.first_line_indent = Pt(0)
    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER if len(caption_text) < 95 else WD_ALIGN_PARAGRAPH.JUSTIFY
    )
    p_cap.paragraph_format.space_before = Pt(1)
    p_cap.paragraph_format.space_after = Pt(6)
    p_cap.paragraph_format.first_line_indent = Pt(0)
    r_cap = p_cap.add_run(f"Fig. {fig_num}. {caption_text}")
    format_run(r_cap, size_pt=8, bold=False, italic=False)


def build_docx():
    doc = docx.Document(TEMPLATE_PATH)

    # Update running headers in all sections to reflect the authors and paper title
    for sec in doc.sections:
        sec.top_margin = Inches(1.18)
        sec.bottom_margin = Inches(1.18)
        sec.left_margin = Inches(1.18)
        sec.right_margin = Inches(1.18)
        for hp in sec.header.paragraphs:
            if "First Author" in hp.text:
                hp.text = (
                    "Ramadhan Et. Al. / J. of ICT. 2026, X (X): 1-10\n"
                    " Early Cart Abandonment Detection Using Big Data\t\t\t\t\t "
                )
                for r in hp.runs:
                    format_run(r, size_pt=8, italic=False)

    # Preserve P00..P15 (Sections 0 and 1 containing Title, Authors, Affiliation, Abstract, Keywords)
    # and remove template instructions from P16 onwards & template tables
    for tbl in list(doc.tables):
        tbl._element.getparent().remove(tbl._element)

    for p in list(doc.paragraphs[16:]):
        p._element.getparent().remove(p._element)

    # --- POPULATE SECTION 0: TITLE & AUTHORS (P00..P10) ---
    # P00: Title (24 pt Centered, capitalize every word except short minor words)
    p_title = doc.paragraphs[0]
    p_title.clear()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run(
        "Comparative Analysis of Batch and Near Real-Time Processing for Early Cart Abandonment Detection in E-Commerce Platforms Using Big Data"
    )
    format_run(r_t, size_pt=24, bold=False)

    # P01: Author names (11 pt Centered with superscripts #1, #2, #3)
    p_auth = doc.paragraphs[1]
    p_auth.clear()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    authors_spec = [
        ("Arief Adhitya Ramadhan ", "#1"),
        (", Muhammad Bafqi ", "#2"),
        (", Zidan Dzulqarnain ", "#3"),
    ]
    for name_str, sup_str in authors_spec:
        rn = p_auth.add_run(name_str)
        format_run(rn, size_pt=11)
        rs = p_auth.add_run(sup_str)
        format_run(rs, size_pt=11, superscript=True)

    # P02: Affiliation (10 pt Italic Centered)
    p_aff1 = doc.paragraphs[2]
    p_aff1.clear()
    p_aff1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_hash = p_aff1.add_run("# ")
    format_run(r_hash, size_pt=10, superscript=True)
    r_dept = p_aff1.add_run("School of Vocational Studies, IPB University")
    format_run(r_dept, size_pt=10, italic=True)

    # P03: Address Including Country Name (10 pt Italic Centered)
    p_addr1 = doc.paragraphs[3]
    p_addr1.clear()
    p_addr1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ad1 = p_addr1.add_run("Bogor, Indonesia")
    format_run(r_ad1, size_pt=10, italic=True)

    # P04, P05, P06: Author emails (9 pt Centered)
    p_em1 = doc.paragraphs[4]
    p_em1.clear()
    p_em1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_run(p_em1.add_run("1 "), size_pt=9, superscript=True)
    format_run(p_em1.add_run("ariefadhitya@apps.ipb.ac.id"), size_pt=9)

    p_em2 = doc.paragraphs[5]
    p_em2.clear()
    p_em2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_run(p_em2.add_run("2 "), size_pt=9, superscript=True)
    format_run(p_em2.add_run("muhammadbafqi@apps.ipb.ac.id"), size_pt=9)

    p_em3 = doc.paragraphs[6]
    p_em3.clear()
    p_em3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_run(p_em3.add_run("3 "), size_pt=9, superscript=True)
    format_run(p_em3.add_run("zidandzulqarnain@apps.ipb.ac.id"), size_pt=9)

    # Clear unused second company lines P07, P08, P09
    for idx in (7, 8, 9):
        doc.paragraphs[idx].clear()
        doc.paragraphs[idx].paragraph_format.space_before = Pt(0)
        doc.paragraphs[idx].paragraph_format.space_after = Pt(0)

    # Remove empty paragraphs P07 and P08 to keep header compact while keeping P11 (sectPr) intact
    doc.paragraphs[8]._element.getparent().remove(doc.paragraphs[8]._element)
    doc.paragraphs[7]._element.getparent().remove(doc.paragraphs[7]._element)

    # Find Abstract heading & body paragraphs dynamically
    idx_abs = next(i for i, p in enumerate(doc.paragraphs) if p.text.strip() == "Abstract")
    p_abs_head = doc.paragraphs[idx_abs]
    p_abs_head.clear()
    p_abs_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ah = p_abs_head.add_run("Abstract")
    format_run(r_ah, size_pt=9, bold=True, italic=True)

    p_abs_body = doc.paragraphs[idx_abs + 1]
    p_abs_body.clear()
    p_abs_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abstract_text = (
        "Cart abandonment represents a critical revenue leakage in e-commerce platforms, particularly "
        "during high-traffic promotional campaigns. Traditional batch processing pipelines often fail "
        "to detect at-risk sessions before users leave the platform. This study investigates early cart "
        "abandonment detection at the first add-to-cart event and evaluates the operational trade-off "
        "between batch and near real-time processing architectures. Using the Retailrocket clickstream "
        "dataset comprising 2,756,101 events and 20,275,902 item property records, we constructed "
        "43,924 cart sessions with a 30-minute inactivity threshold (72.83% abandoned). Ten strictly "
        "anti-leakage behavioral, product, and temporal features were extracted and evaluated using "
        "chronological 80:20 splitting across Random Forest and Logistic Regression classifiers. "
        "Experimental results show that Random Forest achieves the highest discriminative performance "
        "with a Precision of 0.8175, ROC-AUC of 0.7030, PR-AUC of 0.8574, and Balanced Accuracy of "
        "0.6389, while prior session history (prev_sessions), elapsed time to cart (elapsed_min), and "
        "log item price (price_log) emerge as the primary predictors. Latency simulations demonstrate "
        "that daily batch (86,400 s) and hourly batch (3,600 s) reduce Effective Recall to 0.0176 and "
        "0.3909, whereas micro-batch (300 s) and near real-time streaming preserve the full 0.7095 "
        "Effective Recall with a 1.2735 s mean end-to-end streaming latency."
    )
    r_ab = p_abs_body.add_run(abstract_text)
    format_run(r_ab, size_pt=9, bold=True, italic=False)

    p_kw = doc.paragraphs[idx_abs + 2]
    p_kw.clear()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_kw_label = p_kw.add_run("Keywords: ")
    format_run(r_kw_label, size_pt=9, bold=True, italic=False)
    r_kw_body = p_kw.add_run(
        "batch processing, big data analytics, cart abandonment, clickstream classification, "
        "e-commerce, near real-time streaming, random forest"
    )
    format_run(r_kw_body, size_pt=9, bold=False, italic=True)

    # --- SECTION I: INTRODUCTION ---
    add_level1_heading(doc, "I. Introduction")

    add_body_paragraph(
        doc,
        "Perdagangan elektronik (*e-commerce*) modern menghasilkan aliran data interaksi pengguna (*clickstream*) "
        "berkecepatan dan bervolume tinggi setiap detiknya, mulai dari penelusuran halaman produk (*view*), "
        "penambahan produk ke keranjang belanja (*add-to-cart*), hingga penyelesaian pembayaran (*transaction*) "
        "[1], [2]. Meskipun trafik kunjungan dan aktivitas keranjang belanja terus meningkat—terutama pada "
        "periode kampanye belanja nasional dan *flash sale*—mayoritas sesi keranjang belanja justru berakhir "
        "tanpa transaksi, sebuah fenomena yang dikenal sebagai *shopping cart abandonment* [3], [4]. Studi "
        "industri maupun literatur akademik secara konsisten melaporkan bahwa tingkat *cart abandonment* pada "
        "platform ritel daring berkisar antara 65% hingga lebih dari 80% [4], [5]. Pengguna sering kali "
        "menggunakan keranjang belanja sebagai alat pembanding harga, ruang simpan sementara (*wish list*), "
        "atau meninggalkan sesi akibat hambatan harga dan waktu tunggu keputusan [6].",
        drop_cap_first_word=True,
    )

    add_level2_heading(doc, "A. Problem Context and Operational Latency Bottleneck")

    add_body_paragraph(
        doc,
        "Bagi tim pemasaran dan *Customer Relationship Management* (CRM), kemampuan untuk mendeteksi secara dini "
        "sesi pengguna yang berpotensi meninggalkan keranjang merupakan kunci untuk meluncurkan intervensi tepat "
        "waktu, seperti pengingat instan (*push notification*), penawaran kupon terbatas, atau bantuan layanan "
        "pelanggan otomatis [7]. Namun, nilai bisnis dari prediksi *machine learning* pada kasus ini sangat "
        "bergantung pada dua dimensi yang saling mengikat: akurasi klasifikasi pada titik observasi awal dan "
        "kecepatan sistem pemrosesan data (*pipeline latency*) dalam menghasilkan keputusan sebelum pengguna "
        "benar-benar meninggalkan sesi [8], [9].",
    )

    add_body_paragraph(
        doc,
        "Sebagian besar infrastruktur analitik e-commerce konvensional masih mengandalkan pemrosesan berkala "
        "(*batch processing*), di mana log interaksi dikumpulkan dan dieksekusi setiap satu jam atau satu hari "
        "sekali menggunakan penjadwalan *batch* [8]. Pendekatan ini menimbulkan masalah struktural: ketika model "
        "analitik baru menyelesaikan inferensi pada akhir jendela *batch*, sesi pengguna yang bersangkutan telah "
        "lama berakhir (*expired*), sehingga intervensi pemasaran kehilangan relevansi operasionalnya [9], [10]. "
        "Di sisi lain, penelitian terdahulu di bidang prediksi *cart abandonment* umumnya hanya mengevaluasi "
        "performa model secara statis (*offline accuracy/AUC*) atau menggunakan fitur dari keseluruhan sesi yang "
        "baru diketahui setelah sesi berakhir (*post-session features*), yang secara metodologis menimbulkan "
        "kebocoran informasi masa depan (*data leakage*) [5], [11].",
    )

    add_level2_heading(doc, "B. Proposed Solution and Study Objectives")

    add_body_paragraph(
        doc,
        "Penelitian ini mengusulkan rancangan dan evaluasi pipeline deteksi dini *cart abandonment* berbasis "
        "*Lambda Architecture* yang membandingkan pemrosesan *batch* dan *near real-time* (*micro-batch streaming*) "
        "pada dataset clickstream nyata Retailrocket. Secara spesifik, penelitian ini memiliki tiga tujuan utama:",
    )

    add_level3_paragraph(
        doc,
        "1) Strict Anti-Leakage Early Feature Engineering:",
        "Merancang skema ekstraksi 10 fitur perilaku, produk, dan temporal yang sepenuhnya bebas *data leakage* "
        "pada titik observasi *add-to-cart* pertama, termasuk perhitungan riwayat sesi kumulatif yang ketat "
        "dan pembagian data kronologis (*time-based split* 80:20).",
    )
    add_level3_paragraph(
        doc,
        "2) Imbalanced Classification and Driver Identification:",
        "Mengevaluasi performa klasifikasi *Random Forest* dan *Logistic Regression* pada kondisi ketimpangan "
        "kelas (*class imbalance*) menggunakan metrik *Precision, Recall, F1-Score, ROC-AUC, Precision-Recall AUC "
        "(PR-AUC)*, dan *Balanced Accuracy*, serta mengidentifikasi faktor penyebab utama melalui *feature importance*.",
    )
    add_level3_paragraph(
        doc,
        "3) Architectural Latency and Effective Recall Quantification:",
        "Merumuskan dan menyimulasikan metrik *Effective Recall* pada lima skenario jendela waktu pemrosesan "
        "(Batch Harian 86.400 detik, Batch Per Jam 3.600 detik, Micro-Batch 300 detik, Near Real-Time 60 detik, "
        "dan Near Real-Time 10 detik) serta menguji latensi *end-to-end* pada *micro-batch streaming runner* "
        "dengan *trigger* 2 detik.",
    )

    # --- SECTION II: LITERATURE REVIEW ---
    add_level1_heading(doc, "II. Literature Review")

    add_body_paragraph(
        doc,
        "Kajian literatur mengenai analisis *cart abandonment* pada platform e-commerce berakar pada dua ranah "
        "penelitian utama: pemodelan perilaku konsumen berbasis *clickstream* dengan pembelajaran mesin "
        "(*machine learning*), serta arsitektur pemrosesan *Big Data* untuk analitik waktu nyata (*real-time* vs. "
        "*batch*). Pada ranah perilaku konsumen, Kukar-Kinney dan Close [3] menunjukkan bahwa konsumen daring "
        "sering menempatkan barang ke dalam keranjang bukan semata-mata untuk membeli saat itu juga, melainkan "
        "untuk keperluan riset harga, pengorganisasian belanja, dan hiburan. Rubin et al. [4] serta Zhao et al. "
        "[6] memperluas temuan tersebut dengan membuktikan bahwa keraguan pada tahap keranjang (*checkout "
        "hesitancy*) sangat dipengaruhi oleh durasi eksplorasi produk, harga relatif terhadap kategori, dan "
        "waktu akses. Dalam konteks *clickstream*, Moe [1] dan Montgomery et al. [2] mempelopori pemodelan jalur "
        "navigasi (*path analysis*) untuk membedakan pengunjung yang sekadar melihat-lihat (*browsers*) dengan "
        "pengunjung yang memiliki niat beli tinggi (*buyers*).",
    )

    add_body_paragraph(
        doc,
        "Seiring berkembangnya algoritma pembelajaran mesin, sejumlah peneliti menerapkan model klasifikasi "
        "dan *ensemble* untuk memprediksi konversi sesi e-commerce. Baumann et al. [7] dan Cirqueira et al. [11] "
        "mengevaluasi berbagai algoritma *supervised learning* pada data log sesi untuk memprediksi *customer "
        "purchase intent* dan *cart abandonment*, serta menemukan bahwa algoritma berbasis pohon keputusan "
        "(*tree-based ensembles* seperti *Random Forest* dan *Gradient Boosting*) mengungguli model linear "
        "karena mampu menangkap interaksi non-linear antara frekuensi klik, variasi item, dan atribut harga. "
        "Selain itu, Saito dan Rehmsmeier [12] menegaskan bahwa pada dataset dengan ketimpangan kelas "
        "(*imbalanced dataset*), kurva *Precision-Recall* (PR-AUC) memberikan gambaran kinerja yang jauh lebih "
        "akurat dibandingkan ROC-AUC semata. Meskipun demikian, studi prediksi clickstream seperti pada [5], "
        "[10], dan [11] umumnya mengekstraksi fitur agregat dari keseluruhan sesi yang secara praktis belum "
        "tersedia ketika pengguna baru saja menekan tombol *add-to-cart*.",
    )

    add_body_paragraph(
        doc,
        "Pada ranah arsitektur *Big Data*, Marz dan Warren [8] memperkenalkan *Lambda Architecture* yang "
        "memisahkan jalur pemrosesan menjadi *batch layer* (untuk akurasi historis dan pelatihan ulang model di "
        "atas *data lake* bervolume besar) dan *speed layer* (untuk inferensi berlatensi rendah). Armbrust et al. "
        "[9] melalui *Structured Streaming* menunjukkan bahwa pemrosesan aliran data berbasis *micro-batch* "
        "mampu menekan latensi *end-to-end* hingga skala detik sembari mempertahankan konsistensi *fault-tolerance*. "
        "Berdasarkan sintesis literatur di atas, kesenjangan penelitian (*research gap*) yang dijawab oleh studi "
        "ini adalah: (1) belum adanya pemodelan *cart abandonment* pada dataset Retailrocket yang menerapkan "
        "titik potong observasi dini (*first add-to-cart*) dengan aturan *anti-leakage* lintas sesi yang ketat, "
        "dan (2) belum adanya evaluasi terpadu yang mengukur degradasi *Effective Recall* dari arsitektur *batch* "
        "harian/jam menuju *micro-batch* dan *near real-time*.",
    )

    # --- SECTION III: RESEARCH METHOD ---
    add_level1_heading(doc, "III. Research Method")

    add_level2_heading(doc, "A. Experimental Environment and Dataset Description")

    add_body_paragraph(
        doc,
        "Seluruh eksperimen pemrosesan data, pelatihan model, dan pengujian *micro-batch streaming* dieksekusi "
        "secara lokal pada lingkungan perangkat keras dan perangkat lunak dengan spesifikasi terukur: prosesor "
        "12th Gen Intel(R) Core(TM) i5-12450HX (8 *physical cores*, 12 *logical threads*), kapasitas memori "
        "utama 11,78 GB RAM, sistem operasi Windows 10 (Build 26300), serta lingkungan terisolasi Python 3.11.9 "
        "(*pandas* 3.1.1, *numpy* 2.4.6, *scikit-learn* 1.9.1, dan *matplotlib* 3.11.2). Pencatatan spesifikasi "
        "ini memastikan bahwa pengukuran waktu pelatihan (*training time*) dan latensi inferensi per baris "
        "(*inference latency in milliseconds*) memiliki tolok ukur (*baseline*) yang objektif.",
    )

    add_body_paragraph(
        doc,
        "Dataset yang digunakan adalah Retailrocket E-Commerce Dataset, yaitu kumpulan data *clickstream* dunia "
        "nyata yang dikumpulkan selama periode 4,5 bulan (3 Mei 2015 pukul 03:00:04 UTC hingga 18 September 2015 "
        "pukul 02:59:47 UTC). Dataset ini mencakup tiga berkas utama: (1) *events.csv* yang memuat 2.756.101 "
        "rekaman interaksi dari 1.407.580 pengunjung unik terhadap 235.061 produk unik (2.664.312 *view* atau "
        "96,67%, 69.332 *addtocart* atau 2,52%, dan 22.457 *transaction* atau 0,81%); (2) *item_properties_part1.csv* "
        "dan *item_properties_part2.csv* yang memuat 20.275.902 baris atribut produk lintas waktu untuk 417.053 "
        "item unik, di mana properti *categoryid* dan properti *790* (harga produk) diekstraksi; serta (3) "
        "*category_tree.csv* yang berisi 1.669 relasi hierarki kategori.",
    )

    add_level2_heading(doc, "B. Session-ization and Target Labeling")

    add_body_paragraph(
        doc,
        "Karena data mentah *events.csv* tidak menyediakan pengenal sesi (*session_id*), langkah pertama dalam "
        "pipeline adalah melakukan *session-ization*. Rekaman diurutkan secara menaik berdasarkan *visitorid* dan "
        "waktu kejadian dalam detik (*ts = timestamp // 1000*). Mengikuti standar analitik web [2], [5], sebuah "
        "sesi baru terbentuk apabila terjadi pergantian *visitorid* atau terdapat jeda inaktivitas lebih dari "
        "30 menit (GAP = 1.800 detik) antara dua aktivitas berurutan dari pengunjung yang sama. Proses ini "
        "menghasilkan 1.761.660 sesi. Populasi target difilter pada sesi yang memiliki sedikitnya satu aktivitas "
        "*addtocart*, yaitu sebanyak 43.924 sesi. Sesi diberi label *abandoned = 1* apabila tidak memiliki "
        "aktivitas *transaction* hingga sesi berakhir (31.992 sesi atau 72,83%), dan *abandoned = 0* apabila "
        "memiliki sedikitnya satu *transaction* dalam sesi yang sama (11.932 sesi atau 27,17%).",
    )

    add_level2_heading(doc, "C. Strict Anti-Leakage Feature Engineering and Chronological Split")

    add_body_paragraph(
        doc,
        "Agar model dapat diterapkan untuk intervensi dini di dunia nyata, prediksi harus dilakukan tepat ketika "
        "pengguna memasukkan barang pertama ke keranjang. Titik observasi (*observation point*) ditetapkan pada "
        "kejadian *addtocart* pertama di setiap sesi (t_cart). Seluruh aktivitas yang terjadi setelah t_cart di "
        "dalam sesi tersebut dihapus dari perhitungan fitur untuk mencegah *intra-session data leakage*. Sepuluh "
        "fitur input diekstraksi pada titik t_cart: (1) *n_events_before* (jumlah event hingga *addtocart* "
        "pertama), (2) *n_views_before* (jumlah *view* sebelum *addtocart* pertama), (3) *n_unique_items* "
        "(jumlah item unik yang dilihat), (4) *n_views_same_item* (frekuensi melihat item yang dimasukkan ke "
        "keranjang), (5) *elapsed_min* (durasi menit dari awal sesi ke t_cart), (6) *hour* (jam terjadinya "
        "t_cart, 0–23 UTC), (7) *dow* (hari dalam minggu, 0 = Senin s.d. 6 = Minggu), (8) *price_log* "
        "(transformasi ln(1 + price) dari properti 790), (9) *cat_freq* (*frequency encoding* dari *categoryid*), "
        "dan (10) *prev_sessions* (jumlah sesi masa lalu dari *visitorid* yang sama yang dihitung dengan aturan "
        "jendela kumulatif ketat di mana waktu selesai sesi sebelumnya harus lebih kecil dari t_cart sesi saat ini).",
    )

    add_body_paragraph(
        doc,
        "Selanjutnya, untuk mencegah *inter-session data leakage*, seluruh 43.924 sesi diurutkan secara kronologis "
        "berdasarkan t_cart dan dibagi menjadi 80% data Pelatihan (35.139 sesi; rasio *abandoned* 72,75%) dan "
        "20% data Pengujian (8.785 sesi; rasio *abandoned* 73,16%). Nilai hilang pada atribut harga dan kategori "
        "(masing-masing 1,18%) diimputasi menggunakan median harga dari data Pelatihan (59.268,0), dan frekuensi "
        "kategori (*cat_freq*) dihitung murni dari distribusi data Pelatihan.",
    )

    add_level2_heading(doc, "D. Classification Models and Latency Simulation Formulation")

    add_body_paragraph(
        doc,
        "Kami membandingkan dua algoritma klasifikasi: (1) *Random Forest* dengan 200 pohon keputusan "
        "(*n_estimators = 200*, *max_depth = 12*, *class_weight = balanced*), dan (2) *Logistic Regression* "
        "terstandarisasi (*StandardScaler*, *max_iter = 1000*, *class_weight = balanced*). Mengingat ketimpangan "
        "kelas positif yang dominan (73,16% pada data uji), evaluasi menyertakan *Precision-Recall AUC (PR-AUC)* "
        "dan *Balanced Accuracy* di samping *Precision, Recall, F1-Score*, dan *ROC-AUC* [12]. Untuk mengevaluasi "
        "dampak latensi arsitektur, waktu keluarnya keputusan prediksi (t_decision) pada jendela pemrosesan "
        "berkala W dalam satuan detik dan waktu inferensi t_infer dirumuskan pada (1):",
    )

    add_equation_row(doc, "t_decision = ( floor( t_cart / W ) + 1 ) × W + t_infer", "(1)")

    add_body_paragraph(
        doc,
        "Sebuah sesi dianggap masih dapat diintervensi (*reachable*) apabila keputusan prediksi keluar sebelum "
        "sesi pengguna berakhir (t_end) ditambah ambang batas inaktivitas 30 menit (GAP = 1.800 detik), sehingga "
        "batas waktu intervensi (t_deadline) dirumuskan pada (2):",
    )

    add_equation_row(doc, "t_deadline = t_end + GAP", "(2)")

    add_body_paragraph(
        doc,
        "Prediksi *True Positive* (sesi aktual *abandoned* yang berhasil ditebak positif oleh model) yang baru "
        "selesai diproses melewati t_deadline dianggap terlambat karena pengguna telah meninggalkan platform. "
        "Oleh karena itu, metrik *Effective Recall* dirumuskan secara eksplisit pada (3):",
    )

    add_equation_row(
        doc,
        "Effective Recall = TP_detected_before_deadline / ( TP + FN )",
        "(3)",
    )

    # --- SECTION IV: RESULTS AND DISCUSSION ---
    add_level1_heading(doc, "IV. Results And Discussion")

    add_level2_heading(doc, "A. Descriptive Statistics and Behavioral Characteristics")

    add_body_paragraph(
        doc,
        "Dari total 1.761.660 sesi yang terbentuk melalui *session-ization* berambang 30 menit, sebanyak 43.924 "
        "sesi (2,49%) mencapai tahap penambahan produk ke keranjang (*addtocart*), di mana 31.992 sesi (72,83%) "
        "berakhir sebagai *cart abandonment* dan 11.932 sesi (27,17%) berlanjut hingga transaksi selesai. Pada "
        "data pengujian (8.785 sesi), median sisa waktu sesi setelah *addtocart* pertama (t_end − t_cart) sangat "
        "singkat, yakni hanya 85,0 detik (rata-rata 551,72 detik atau 9,2 menit). Selain itu, pengunjung yang "
        "menyelesaikan transaksi memiliki rata-rata riwayat sesi masa lalu (*prev_sessions*) jauh lebih tinggi "
        "(9,44 sesi) dibandingkan pelaku *abandonment* (2,20 sesi), serta durasi eksplorasi sebelum *addtocart* "
        "(*elapsed_min*) lebih panjang (8,89 menit vs. 4,26 menit). Hal ini mengonfirmasi bahwa tindakan "
        "memasukkan barang ke keranjang secara tergesa-gesa di awal sesi sering kali berfungsi sebagai penanda "
        "sementara (*bookmark*), bukan niat menyelesaikan pembayaran.",
    )

    add_level2_heading(doc, "B. Classification Performance and Imbalance Evaluation")

    add_body_paragraph(
        doc,
        "Perbandingan kinerja model *Random Forest* dan *Logistic Regression* pada 8.785 sesi data uji "
        "menggunakan ambang probabilitas standar (0,50) disajikan pada Table I.",
    )

    add_inista_table(
        doc,
        "I",
        "Comparison of Classification Performance on Chronological Test Set (8,785 Sessions)",
        [
            "Model",
            "Precision",
            "Recall",
            "F1-Score",
            "ROC-AUC",
            "PR-AUC",
            "Balanced Acc",
            "Train (s)",
            "Infer (ms/row)",
        ],
        [
            [
                "**Random Forest**",
                "**0.8175**",
                "0.7095",
                "0.7597",
                "**0.7030**",
                "**0.8574**",
                "**0.6389**",
                "1.0011",
                "0.006635",
            ],
            [
                "Logistic Regression",
                "0.8036",
                "**0.7487**",
                "**0.7752**",
                "0.6829",
                "0.8420",
                "0.6250",
                "**0.0479**",
                "**0.000228**",
            ],
        ],
    )

    add_body_paragraph(
        doc,
        "Berdasarkan Table I, *Random Forest* mengungguli *Logistic Regression* pada seluruh metrik diskriminasi "
        "lintas ambang dan metrik ketimpangan kelas, yaitu ROC-AUC (0,7030 vs. 0,6829), PR-AUC (0,8574 vs. "
        "0,8420), *Balanced Accuracy* (0,6389 vs. 0,6250), dan *Precision* (0,8175 vs. 0,8036). Tingginya nilai "
        "PR-AUC (0,8574) membuktikan bahwa meskipun kelas positif mendominasi 73,16% populasi uji, *Random Forest* "
        "mampu menjaga presisi prediksi positif secara konsisten. Waktu inferensi *Random Forest* sebesar "
        "0,006635 ms/baris setara dengan kapasitas sekitar 150.000 prediksi per detik pada prosesor Intel Core "
        "i5-12450HX, sehingga tidak menjadi penghambat pada arsitektur *near real-time*. Evaluasi sensitivitas "
        "ambang keputusan disajikan pada Table II.",
    )

    add_inista_table(
        doc,
        "II",
        "Threshold Sensitivity Analysis for Random Forest and Logistic Regression",
        ["Model", "Threshold", "Precision", "Recall", "F1-Score", "Balanced Accuracy"],
        [
            ["Random Forest", "0.30", "0.7551", "**0.9818**", "**0.8536**", "0.5568"],
            ["Random Forest", "0.40", "0.7751", "0.9136", "0.8387", "0.5955"],
            ["Random Forest", "0.50", "0.8175", "0.7095", "0.7597", "**0.6389**"],
            ["Random Forest", "0.60", "0.8771", "0.4176", "0.5658", "0.6291"],
            ["Random Forest", "0.70", "**0.9055**", "0.2533", "0.3959", "0.5906"],
            ["Logistic Regression", "0.30", "0.7584", "0.9687", "0.8508", "0.5639"],
            ["Logistic Regression", "0.40", "0.7694", "0.9225", "0.8390", "0.5845"],
            ["Logistic Regression", "0.50", "0.8036", "0.7487", "0.7752", "0.6250"],
            ["Logistic Regression", "0.60", "0.8690", "0.2983", "0.4441", "0.5879"],
            ["Logistic Regression", "0.70", "0.9369", "0.0300", "0.0582", "0.5123"],
        ],
    )

    add_body_paragraph(
        doc,
        "Table II memperlihatkan bahwa untuk intervensi berbiaya rendah (seperti *pop-up reminder* di layar), "
        "menurunkan ambang *Random Forest* ke 0,40 meningkatkan *Recall* menjadi 91,36% dan *F1-Score* menjadi "
        "0,8387 dengan *Precision* 77,51%. Sebaliknya, apabila intervensi melibatkan subsidi margin finansial "
        "(seperti voucer diskon langsung), penggunaan ambang 0,50 atau 0,60 memaksimalkan *Balanced Accuracy* "
        "(0,6389) dan meningkatkan *Precision* hingga 87,71%, sehingga meminimalkan pemberian diskon sia-sia "
        "kepada pengguna yang sebenarnya tetap akan membeli (*False Positive*).",
    )

    add_level2_heading(doc, "C. Key Drivers of Cart Abandonment and Temporal Patterns")

    add_body_paragraph(
        doc,
        "Untuk menjawab pertanyaan analitik mengenai faktor penyebab *cart abandonment*, bobot *Gini feature "
        "importance* dari model *Random Forest* divisualisasikan pada Fig. 1, sedangkan pola tingkat "
        "*abandonment* lintas jam dan hari ditampilkan pada Fig. 2.",
    )

    add_inista_figure(
        doc,
        1,
        os.path.join(FIG_DIR, "fig1_feature_importance.png"),
        "Relative feature importance (Gini importance) of the Random Forest model at the first add-to-cart observation point.",
        width_in=5.4,
    )

    add_body_paragraph(
        doc,
        "Sebagaimana ditunjukkan pada Fig. 1, tiga prediktor paling dominan menyumbang lebih dari 51% total daya "
        "pisah model: *prev_sessions* (0,1995), *elapsed_min* (0,1600), dan *price_log* (0,1515), diikuti oleh "
        "*cat_freq* (0,1277) dan *hour* (0,1016). Rata-rata *price_log* pada sesi *abandoned* (11,0910) lebih "
        "tinggi dibandingkan sesi *completed* (11,0364), mengindikasikan sensitivitas harga saat barang sudah "
        "berada di dalam keranjang.",
    )

    add_inista_figure(
        doc,
        2,
        os.path.join(FIG_DIR, "fig2_temporal_patterns.png"),
        "Empirical cart abandonment rates across (a) hours of the day (UTC) and (b) days of the week.",
        width_in=5.8,
    )

    add_body_paragraph(
        doc,
        "Fig. 2(a) menunjukkan bahwa tingkat *abandonment* mencapai titik tertinggi pada rentang pukul 08:00–12:00 "
        "UTC dengan puncak pada pukul 09:00 UTC (85,84%) dan 12:00 UTC (85,09%), sementara konversi transaksi "
        "terbaik terjadi pada pukul 15:00 UTC (64,73%). Adapun Fig. 2(b) memperlihatkan bahwa tingkat "
        "*abandonment* meningkat signifikan pada akhir pekan, mencapai puncaknya pada hari Sabtu (77,39%) dan "
        "Minggu (76,55%), sedangkan hari kerja pertengahan minggu seperti Rabu (69,88%) mencatatkan tingkat "
        "penyelesaian transaksi yang lebih tinggi.",
    )

    add_level2_heading(doc, "D. Batch vs. Near Real-Time Latency and Effective Recall Evaluation")

    add_body_paragraph(
        doc,
        "Perbandingan efektivitas deteksi ketika model *Random Forest* yang sama dijalankan di bawah lima "
        "skenario jendela pemrosesan arsitektur disajikan pada Table III dan divisualisasikan pada Fig. 3.",
    )

    add_inista_table(
        doc,
        "III",
        "Simulation of Processing Latency and Effective Recall Across Architectural Windows",
        [
            "Processing Mode",
            "Window W (s)",
            "Mean Latency (s)",
            "Median Latency (s)",
            "Before Deadline (%)",
            "Timely TP Count",
            "Effective Recall",
        ],
        [
            [
                "Batch Harian (24 Jam)",
                "86,400",
                "37,343.62",
                "26,765.00",
                "3.60%",
                "113 / 6,427",
                "**0.0176**",
            ],
            [
                "Batch Per Jam (1 Jam)",
                "3,600",
                "1,792.34",
                "1,788.00",
                "60.47%",
                "2,512 / 6,427",
                "**0.3909**",
            ],
            [
                "**Micro-Batch (5 Menit)**",
                "300",
                "150.21",
                "149.00",
                "**100.00%**",
                "**4,560 / 6,427**",
                "**0.7095**",
            ],
            [
                "**Near Real-Time (1 Menit)**",
                "60",
                "30.51",
                "30.00",
                "**100.00%**",
                "**4,560 / 6,427**",
                "**0.7095**",
            ],
            [
                "**Near Real-Time (10 Detik)**",
                "10",
                "5.52",
                "5.00",
                "**100.00%**",
                "**4,560 / 6,427**",
                "**0.7095**",
            ],
        ],
    )

    add_inista_figure(
        doc,
        3,
        os.path.join(FIG_DIR, "fig3_latency_effective_recall.png"),
        "Comparison of Effective Recall (%) and percentage of decisions completed before the session intervention deadline across five processing windows.",
        width_in=5.4,
    )

    add_body_paragraph(
        doc,
        "Data pada Table III dan Fig. 3 membuktikan secara kuantitatif bagaimana keterlambatan arsitektur "
        "menggerus nilai guna model *Machine Learning*. Pada skenario Batch Harian (W = 86.400 detik), rata-rata "
        "latensi mencapai 37.343,62 detik (10,37 jam) sehingga hanya 3,60% sesi yang keputusannya keluar sebelum "
        "batas waktu intervensi, menjatuhkan *Effective Recall* dari 0,7095 menjadi 0,0176 (kehilangan 97,5% "
        "potensi intervensi). Pada Batch Per Jam (W = 3.600 detik), sebanyak 39,53% sesi telah melewati batas "
        "intervensi sehingga *Effective Recall* menyusut hampir separuhnya menjadi 0,3909. Sebaliknya, ketika "
        "jendela pemrosesan diperkecil ke *Micro-Batch* 5 menit (300 detik) hingga *Near Real-Time* 10 detik, "
        "100% keputusan selesai sebelum batas waktu intervensi dan mempertahankan *Effective Recall* penuh "
        "sebesar 0,7095. Hasil pengujian *micro-batch streaming* dengan *trigger* 2 detik terhadap 1.000 sesi "
        "uji dirangkum pada Table IV.",
    )

    add_inista_table(
        doc,
        "IV",
        "End-to-End Latency Distribution of Micro-Batch Streaming Benchmark (1,000 Streamed Sessions, 2-Second Trigger)",
        ["Streaming Benchmark Metric", "Measured Value"],
        [
            [
                "Streaming Execution Mode",
                "Micro-Batch File Streaming (Atomic Rename, 2s Trigger)",
            ],
            ["Total Streamed Sessions / Micro-Batches", "1,000 rows across 7 active micro-batches"],
            ["Mean End-to-End Latency (s)", "**1.2735 s**"],
            ["Standard Deviation Latency (s)", "0.6053 s"],
            ["Minimum / 25th Percentile Latency (s)", "0.4980 s / 0.5571 s"],
            ["Median (50th Percentile) Latency (s)", "**1.2596 s**"],
            ["75th Percentile / Maximum Latency (s)", "2.0006 s / **2.0766 s**"],
            ["Mean Batch Model Inference Time (ms)", "28.9815 ms"],
        ],
    )

    add_body_paragraph(
        doc,
        "Sebagaimana terlihat pada Table IV, pipeline *micro-batch streaming* ber-trigger 2 detik mencapai "
        "rata-rata latensi *end-to-end* sebesar 1,2735 detik (median 1,2596 detik, maksimum 2,0766 detik) dengan "
        "rata-rata waktu inferensi *batch* hanya 28,98 ms. Empat keterbatasan metodologis yang perlu dicatat "
        "meliputi: (1) batas waktu intervensi 30 menit pasca-sesi merupakan asumsi analitis dari ambang "
        "inaktivitas sesi; (2) atribut harga dan kategori menggunakan rekaman terakhir per item dari "
        "*item_properties*; (3) eksperimen menggunakan satu periode dataset Retailrocket; dan (4) pengujian "
        "streaming menggunakan *atomic file-based micro-batching* pada satu node lokal.",
    )

    # --- SECTION V: CONCLUSION ---
    add_level1_heading(doc, "V. Conclusion")

    add_body_paragraph(
        doc,
        "Penelitian ini berhasil merancang, mengimplementasikan, dan mengevaluasi pipeline deteksi dini "
        "*cart abandonment* berbasis *Big Data* pada dataset clickstream Retailrocket (2.756.101 event; 43.924 "
        "sesi keranjang belanja dengan tingkat *abandonment* 72,83%). Dengan menerapkan aturan *anti-leakage* "
        "ketat pada titik observasi *addtocart* pertama dan pembagian data kronologis 80:20, model *Random Forest* "
        "memberikan kinerja diskriminasi terbaik dengan *Precision* 0,8175, ROC-AUC 0,7030, PR-AUC 0,8574, dan "
        "*Balanced Accuracy* 0,6389, serta kecepatan inferensi 0,006635 ms/baris. Analisis *feature importance* "
        "mengungkap bahwa riwayat sesi pengunjung (*prev_sessions* = 0,1995), durasi menuju keranjang "
        "(*elapsed_min* = 0,1600), dan logaritma harga produk (*price_log* = 0,1515) merupakan determinan utama "
        "*cart abandonment*. Evaluasi arsitektur membuktikan bahwa pemrosesan Batch Harian (24 jam) dan Batch "
        "Per Jam (1 jam) menurunkan *Effective Recall* secara drastis menjadi 0,0176 dan 0,3909 akibat keputusan "
        "yang terlambat melewati batas intervensi sesi. Sebaliknya, arsitektur *Micro-Batch* (5 menit) dan "
        "*Near Real-Time Streaming* (10–60 detik) berhasil mempertahankan 100% keputusan sebelum batas waktu "
        "dengan *Effective Recall* penuh sebesar 0,7095 serta rata-rata latensi *end-to-end streaming* 1,2735 "
        "detik, sehingga sangat direkomendasikan untuk sistem intervensi CRM e-commerce.",
    )

    # --- ACKNOWLEDGMENT (Unnumbered Level-1 Heading in Small Caps) ---
    add_level1_heading(doc, "Acknowledgment")

    add_body_paragraph(
        doc,
        "Para penulis mengucapkan terima kasih kepada tim dosen pengampu mata kuliah Teknologi Big Data di "
        "Sekolah Vokasi Institut Pertanian Bogor (IPB University) atas bimbingan metodologis serta fasilitasi "
        "selama pelaksanaan penelitian ini.",
    )

    # --- REFERENCES (Unnumbered Level-1 Heading in Small Caps, items in 8 pt) ---
    add_level1_heading(doc, "References")

    refs = [
        (
            "[1] W. W. Moe, “Buying, searching, or browsing: Differentiating between online shoppers using in-store navigational clickstream,” ",
            "Journal of Consumer Psychology",
            ", vol. 13, no. 1–2, pp. 29–39, 2003.",
        ),
        (
            "[2] A. L. Montgomery, S. Li, K. Srinivasan, and J. C. Liechty, “Modeling online browsing and path analysis using clickstream data,” ",
            "Marketing Science",
            ", vol. 23, no. 4, pp. 579–595, 2004.",
        ),
        (
            "[3] M. Kukar-Kinney and A. G. Close, “The determinants of consumers’ online shopping cart abandonment,” ",
            "Journal of the Academy of Marketing Science",
            ", vol. 38, no. 2, pp. 240–250, 2010.",
        ),
        (
            "[4] D. Rubin, C. Martins, V. Ilyuk, and L. Hildebrand, “The effects of perceived diagnosticity on online shopping cart abandonment,” ",
            "Journal of Retailing and Consumer Services",
            ", vol. 52, p. 101911, 2020.",
        ),
        (
            "[5] H. Tang, D. Liao, and Z. Sun, “Predicting shopping cart abandonment with deep sequence models on e-commerce clickstream data,” ",
            "IEEE Access",
            ", vol. 8, pp. 134512–134523, 2020.",
        ),
        (
            "[6] H. Zhao, S. Wang, and Y. Chen, “Understanding mobile shopping cart abandonment: An integration of behavioral and contextual factors,” ",
            "Electronic Commerce Research and Applications",
            ", vol. 46, p. 101032, 2021.",
        ),
        (
            "[7] A. Baumann, J. Haupt, F. Gebert, and S. Lessmann, “Changing perspectives: Using graph metrics to predict purchase probabilities in e-commerce,” ",
            "Expert Systems with Applications",
            ", vol. 94, pp. 137–148, 2018.",
        ),
        (
            "[8] N. Marz and J. Warren, ",
            "Big Data: Principles and Best Practices of Scalable Real-Time Data Systems",
            ". Shelter Island, NY, USA: Manning Publications, 2015.",
        ),
        (
            "[9] M. Armbrust, T. Das, J. Torres, B. Yavuz, S. Zhu, R. Xin, A. Ghodsi, I. Stoica, and M. Zaharia, “Structured streaming: A declarative API for real-time applications in Apache Spark,” in ",
            "Proc. ACM SIGMOD Int. Conf. Management of Data",
            ", Houston, TX, USA, 2018, pp. 601–613.",
        ),
        (
            "[10] M. Sakar, S. O. Polat, M. Katircioglu, and Y. Kastro, “Real-time prediction of online shoppers’ purchasing intention using multilayer perceptron and LSTM recurrent neural networks,” ",
            "Neural Computing and Applications",
            ", vol. 31, no. 10, pp. 6893–6908, 2019.",
        ),
        (
            "[11] D. Cirqueira, M. Hofer, D. Nedbal, M. Helfert, and M. Bezbradica, “Customer purchase behavior prediction in e-commerce: A conceptual framework and research agenda,” in ",
            "Proc. Int. Workshop New Frontiers in Mining Complex Patterns (NFMCP)",
            ", Cham, Switzerland: Springer, 2020, pp. 119–136.",
        ),
        (
            "[12] T. Saito and M. Rehmsmeier, “The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets,” ",
            "PLOS ONE",
            ", vol. 10, no. 3, p. e0118432, 2015.",
        ),
    ]

    for pre_txt, italic_venue, post_txt in refs:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Inches(0.25)
        p_ref.paragraph_format.first_line_indent = Inches(-0.25)
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(2)
        format_run(p_ref.add_run(pre_txt), size_pt=8, bold=False, italic=False)
        format_run(p_ref.add_run(italic_venue), size_pt=8, bold=False, italic=True)
        format_run(p_ref.add_run(post_txt), size_pt=8, bold=False, italic=False)

    doc.save(OUTPUT_DOCX)
    print(f"Successfully generated: {OUTPUT_DOCX}")


if __name__ == "__main__":
    build_docx()
