# -*- coding: utf-8 -*-
"""
Generate Widescreen (16:9) PowerPoint Presentation (.pptx) for Kelompok 15
Includes embedded 300-DPI figures, data tables, architectural diagram cards,
and speaker notes for each slide.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = r"c:\Bafqi\Big Data"
FIG_DIR = os.path.join(BASE_DIR, "outputs", "figures")
OUT_PPTX = os.path.join(BASE_DIR, "Presentasi_Big_Data_Kelompok_15.pptx")

# Palette (Editorial Slate & Navy)
C_NAVY = RGBColor(15, 23, 42)       # #0f172a
C_BLUE = RGBColor(15, 76, 129)      # #0f4c81
C_BLUE_SOFT = RGBColor(224, 242, 254)
C_BG = RGBColor(248, 250, 252)      # #f8fafc
C_WHITE = RGBColor(255, 255, 255)
C_TEXT = RGBColor(30, 41, 59)
C_MUTED = RGBColor(100, 116, 139)
C_BORDER = RGBColor(203, 213, 225)
C_RED = RGBColor(185, 28, 28)
C_RED_BG = RGBColor(254, 242, 242)
C_GREEN = RGBColor(4, 120, 87)
C_GREEN_BG = RGBColor(236, 253, 245)
C_AMBER = RGBColor(180, 83, 9)


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(slide, title_text, subtitle_text, slide_num):
    # Top accent bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_BLUE
    bar.line.fill.background()

    # Title box
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.28), Inches(11.0), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title_text
    r.font.name = "Calibri"
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.color.rgb = C_NAVY

    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = subtitle_text
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.color.rgb = C_MUTED

    # Slide number pill
    nb = slide.shapes.add_textbox(Inches(11.7), Inches(0.32), Inches(1.05), Inches(0.4))
    ntf = nb.text_frame
    np_p = ntf.paragraphs[0]
    np_p.alignment = PP_ALIGN.RIGHT
    nr = np_p.add_run()
    nr.text = f"{slide_num:02d} / 11"
    nr.font.name = "Consolas"
    nr.font.size = Pt(11)
    nr.font.bold = True
    nr.font.color.rgb = C_MUTED

    # Divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.18), Inches(12.133), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = C_BORDER
    line.line.fill.background()


def add_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_BORDER):
    rect = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    rect.adjustments[0] = 0.02
    rect.fill.solid()
    rect.fill.fore_color.rgb = bg_color
    if border_color:
        rect.line.color.rgb = border_color
        rect.line.width = Pt(1)
    else:
        rect.line.fill.background()
    return rect


def add_kpi_box(slide, left, top, width, height, label, value, sub, val_color=C_NAVY, bg_color=C_WHITE):
    add_card(slide, left, top, width, height, bg_color=bg_color)
    tb = slide.shapes.add_textbox(Inches(left + 0.18), Inches(top + 0.14), Inches(width - 0.36), Inches(height - 0.28))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = label
    r1.font.name = "Calibri"
    r1.font.size = Pt(11.5)
    r1.font.bold = True
    r1.font.color.rgb = C_MUTED

    p2 = tf.add_paragraph()
    p2.space_before = Pt(4)
    r2 = p2.add_run()
    r2.text = value
    r2.font.name = "Consolas"
    r2.font.size = Pt(25)
    r2.font.bold = True
    r2.font.color.rgb = val_color

    p3 = tf.add_paragraph()
    p3.space_before = Pt(3)
    r3 = p3.add_run()
    r3.text = sub
    r3.font.name = "Calibri"
    r3.font.size = Pt(11)
    r3.font.color.rgb = C_TEXT


def add_bullet_card(slide, left, top, width, height, heading, bullets, bg_color=C_WHITE, head_color=C_BLUE):
    add_card(slide, left, top, width, height, bg_color=bg_color)
    tb = slide.shapes.add_textbox(Inches(left + 0.22), Inches(top + 0.18), Inches(width - 0.44), Inches(height - 0.36))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p0 = tf.paragraphs[0]
    r0 = p0.add_run()
    r0.text = heading
    r0.font.name = "Calibri"
    r0.font.size = Pt(15.5)
    r0.font.bold = True
    r0.font.color.rgb = head_color

    for b_title, b_desc in bullets:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r_b = p.add_run()
        r_b.text = f"▪ {b_title}: " if b_title else "▪ "
        r_b.font.name = "Calibri"
        r_b.font.size = Pt(13)
        r_b.font.bold = True
        r_b.font.color.rgb = C_NAVY

        r_d = p.add_run()
        r_d.text = b_desc
        r_d.font.name = "Calibri"
        r_d.font.size = Pt(13)
        r_d.font.color.rgb = C_TEXT


def style_table(tbl, headers, rows, col_widths_in=None, highlight_row_idx=None):
    for j, h in enumerate(headers):
        if col_widths_in and j < len(col_widths_in):
            tbl.columns[j].width = Inches(col_widths_in[j])
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.name = "Calibri"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = C_WHITE

    for i, row_vals in enumerate(rows):
        is_hl = highlight_row_idx is not None and (i in highlight_row_idx if isinstance(highlight_row_idx, (list, tuple, set)) else i == highlight_row_idx)
        bg = C_BLUE_SOFT if is_hl else (C_WHITE if i % 2 == 0 else C_BG)
        for j, val in enumerate(row_vals):
            cell = tbl.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            r = p.add_run()
            r.text = str(val)
            r.font.name = "Consolas" if j > 0 else "Calibri"
            r.font.size = Pt(11.5)
            r.font.bold = is_hl or (j == 0)
            r.font.color.rgb = C_NAVY if is_hl else C_TEXT


def add_notes(slide, text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: COVER SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, C_NAVY)

    # Top strip
    strip = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    strip.fill.solid()
    strip.fill.fore_color.rgb = RGBColor(56, 189, 248)
    strip.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(3.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p_tag = tf1.paragraphs[0]
    r_tag = p_tag.add_run()
    r_tag.text = "PROYEK AKHIR TEKNOLOGI BIG DATA — KELOMPOK 15"
    r_tag.font.name = "Consolas"
    r_tag.font.size = Pt(13)
    r_tag.font.bold = True
    r_tag.font.color.rgb = RGBColor(56, 189, 248)

    p_title = tf1.add_paragraph()
    p_title.space_before = Pt(14)
    r_title = p_title.add_run()
    r_title.text = "Analisis Perbandingan Pemrosesan Batch dan Near Real-Time dalam Deteksi Dini Cart Abandonment pada Platform E-Commerce"
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(32)
    r_title.font.bold = True
    r_title.font.color.rgb = C_WHITE

    p_sub = tf1.add_paragraph()
    p_sub.space_before = Pt(14)
    r_sub = p_sub.add_run()
    r_sub.text = (
        "Menebak lebih awal pembeli online yang berpotensi batal checkout tepat saat barang pertama masuk keranjang, "
        "serta membuktikan seberapa besar pengaruh kecepatan deteksi (Batch vs. Streaming) terhadap peluang intervensi toko online."
    )
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(15.5)
    r_sub.font.color.rgb = RGBColor(203, 213, 225)

    # Team Cards at bottom
    authors = [
        ("Arief Adhitya Ramadhan", "NIM: J0403241055", "Data Engineering & Arsitektur Lambda"),
        ("Muhammad Bafqi", "NIM: J0403241018", "Machine Learning & Anti-Leakage Pipeline"),
        ("Zidan Dzulqarnain", "NIM: J0403241032", "Evaluasi Latensi, Visualisasi & Laporan"),
    ]
    for i, (name, nim, role) in enumerate(authors):
        left = 0.8 + i * 4.0
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(5.05), Inches(3.75), Inches(1.65))
        card.adjustments[0] = 0.04
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(30, 41, 59)
        card.line.color.rgb = RGBColor(71, 85, 105)
        card.line.width = Pt(1)

        ctb = s1.shapes.add_textbox(Inches(left + 0.2), Inches(5.2), Inches(3.35), Inches(1.35))
        ctf = ctb.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        cr1 = cp1.add_run()
        cr1.text = name
        cr1.font.name = "Calibri"
        cr1.font.size = Pt(16)
        cr1.font.bold = True
        cr1.font.color.rgb = C_WHITE

        cp2 = ctf.add_paragraph()
        cp2.space_before = Pt(4)
        cr2 = cp2.add_run()
        cr2.text = nim
        cr2.font.name = "Consolas"
        cr2.font.size = Pt(12.5)
        cr2.font.color.rgb = RGBColor(56, 189, 248)

        cp3 = ctf.add_paragraph()
        cp3.space_before = Pt(6)
        cr3 = cp3.add_run()
        cr3.text = role
        cr3.font.name = "Calibri"
        cr3.font.size = Pt(12)
        cr3.font.color.rgb = RGBColor(148, 163, 184)

    add_notes(
        s1,
        "Narasi Pembuka (Elevator Pitch):\n"
        "Halo semuanya, kami dari Kelompok 15 (Arief, Bafqi, dan Zidan). Pada proyek Teknologi Big Data ini, kami membuat sistem yang bisa menebak lebih awal pembeli online mana yang kemungkinan besar bakal batal checkout setelah memasukkan barang ke keranjang. Kami memakai data kebiasaan belanja riil dari e-commerce Retailrocket untuk mempelajari pola orang yang akhirnya beli dan yang pergi begitu saja. Kami juga membandingkan dua pendekatan pemrosesan data: secara berkala (batch) dan secara langsung (near real-time/stream), untuk melihat apakah deteksi yang lebih cepat benar-benar memberi toko online kesempatan lebih besar untuk membujuk pembeli lewat pengingat atau promo sebelum mereka pergi."
    )

    # =========================================================================
    # SLIDE 2: INTI MASALAH & MENGAPA KECEPATAN ITU KRUSIAL
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2, C_BG)
    add_header(
        s2,
        "Latar Belakang & Permasalahan Utama",
        "Mengapa akurasi model Machine Learning saja tidak cukup tanpa kecepatan pemrosesan data?",
        2,
    )

    add_kpi_box(s2, 0.6, 1.4, 3.85, 1.45, "TINGKAT CART ABANDONMENT", "72.83%", "31.992 dari 43.924 sesi keranjang batal beli", C_RED, C_RED_BG)
    add_kpi_box(s2, 4.74, 1.4, 3.85, 1.45, "MEDIAN SISA WAKTU SESI", "85.0 Detik", "Waktu tersisa setelah klik add-to-cart pertama", C_BLUE, C_BLUE_SOFT)
    add_kpi_box(s2, 8.88, 1.4, 3.85, 1.45, "TARGET INTERVENSI CRM", "< 30 Menit", "Sebelum sesi pengunjung benar-benar berakhir", C_GREEN, C_GREEN_BG)

    add_bullet_card(
        s2,
        0.6,
        3.1,
        5.9,
        3.9,
        "Masalah di E-Commerce Saat Ini (Terutama Saat Flash Sale)",
        [
            ("Keranjang Hanya Jadi Bookmark", "Mayoritas pengunjung (72,83%) menaruh barang di keranjang hanya untuk bandingkan harga atau simpan sementara, lalu pergi."),
            ("Waktu Tunggu Sangat Sempit", "Dari data riil Retailrocket, setelah pengguna klik add-to-cart pertama, median sisa waktu mereka di web hanya 85 detik (rata-rata 9,2 menit)."),
            ("Kelemahan Pemrosesan Batch Tradisional", "Jika sistem analitik baru memproses data tiap 1 jam atau 24 jam sekali, prediksi baru keluar saat pembeli sudah lama menutup aplikasi."),
            ("Kebocoran Data pada Riset Lama", "Banyak model lama memakai fitur total durasi sesi akhir (yang baru ketahuan setelah user pergi), sehingga tidak bisa dipakai deteksi dini."),
        ],
    )

    add_bullet_card(
        s2,
        6.83,
        3.1,
        5.9,
        3.9,
        "Solusi & Tujuan Proyek Kelompok 15",
        [
            ("Deteksi Dini (Anti-Leakage)", "Menebak risiko batal checkout tepat pada detik barang pertama masuk keranjang (first add-to-cart)."),
            ("Klasifikasi Perilaku Belanja", "Membandingkan algoritma Random Forest (utama) dan Logistic Regression (baseline cepat) pada data timpang (imbalanced)."),
            ("Simulasi Batch vs. Near Real-Time", "Mengukur berapa persen pembeli batal checkout yang benar-benar sempat diselamatkan (Effective Recall) pada jendela 24 jam, 1 jam, 5 menit, 1 menit, hingga 10 detik."),
            ("Uji Streaming Nyata (Speed Layer)", "Menguji pipeline micro-batch streaming dengan trigger 2 detik untuk membuktikan kelayakan operasional."),
        ],
    )

    add_notes(
        s2,
        "Poin Penjelasan Slide 2:\n"
        "- Masalah terbesarnya ada di 3 angka bagian atas: 72,83% keranjang belanja ditinggalkan begitu saja, dan setelah klik 'add-to-cart' pertama, median pengunjung hanya bertahan 85 detik di dalam web.\n"
        "- Kalau toko online memakai sistem Batch (misal dihitung tiap malam atau tiap 1 jam), saat sistem tahu 'Oh user A mau batal beli', user A sudah pergi dari tadi.\n"
        "- Karena itu kami menggabungkan Machine Learning pada titik add-to-cart pertama dengan perbandingan arsitektur Batch vs Near Real-Time."
    )

    # =========================================================================
    # SLIDE 3: DATASET RETAILROCKET & KARAKTERISTIK BIG DATA
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3, C_BG)
    add_header(
        s3,
        "Dataset Clickstream Nyata: Retailrocket E-Commerce",
        "Rekaman interaksi asli selama 4,5 bulan (Mei–September 2015) tanpa data sintetis",
        3,
    )

    add_kpi_box(s3, 0.6, 1.4, 2.85, 1.35, "TOTAL CLICKSTREAM EVENTS", "2,756,101", "96,7% view · 2,5% cart · 0,8% tx")
    add_kpi_box(s3, 3.69, 1.4, 2.85, 1.35, "BARIS PROPERTI PRODUK", "20,275,902", "417.053 item unik lintas waktu")
    add_kpi_box(s3, 6.78, 1.4, 2.85, 1.35, "PENGUNJUNG UNIK", "1,407,580", "Membentuk 1.761.660 total sesi")
    add_kpi_box(s3, 9.87, 1.4, 2.86, 1.35, "SESI KERANJANG (ANALISIS)", "43,924", "Train: 35.139 (80%) · Test: 8.785 (20%)")

    # Table of dataset files
    t_shape = s3.shapes.add_table(5, 4, Inches(0.6), Inches(3.0), Inches(12.133), Inches(2.2))
    style_table(
        t_shape.table,
        ["Nama Berkas CSV", "Volume Baris / Ukuran", "Struktur Kolom Utama", "Peran dalam Pipeline Big Data"],
        [
            ["events.csv", "2.756.101 baris (~94 MB)", "timestamp, visitorid, event, itemid, transactionid", "Sumber utama session-ization, titik observasi addtocart, dan label transaksi"],
            ["item_properties_part1.csv", "10.999.999 baris (~484 MB)", "timestamp, itemid, property, value", "Ekstraksi atribut produk: harga (properti 790) dan kategori (categoryid)"],
            ["item_properties_part2.csv", "9.275.903 baris (~409 MB)", "timestamp, itemid, property, value", "Bagian ke-2 log perubahan properti produk (total >20,27 juta baris)"],
            ["category_tree.csv", "1.669 baris (~14 KB)", "categoryid, parentid", "Referensi struktur pohon kategori produk e-commerce"],
        ],
        col_widths_in=[2.5, 2.3, 3.3, 4.033],
    )

    add_bullet_card(
        s3,
        0.6,
        5.4,
        12.133,
        1.65,
        "Karakteristik 3V Big Data & Tantangan Teknis Dataset",
        [
            ("Volume & Velocity", "Lebih dari 20,27 juta baris properti item dan 2,75 juta aliran klik yang pada skala produksi terus bertambah setiap detik."),
            ("Variety & Tidak Ada Session ID Bawaan", "Data mentah berupa log event murni tanpa kolom session_id dan harga di-encode string berawalan 'n', sehingga harus dibangun lewat pipeline."),
        ],
    )

    add_notes(
        s3,
        "Poin Penjelasan Slide 3:\n"
        "- Kami menggunakan dataset publik Retailrocket dari Kaggle yang berisi 2,75 juta klik dan lebih dari 20,2 juta baris atribut produk.\n"
        "- Tantangan utamanya: data mentah ini belum punya session_id dan belum punya label cart abandonment. Jadi kami harus merakit sesi sendiri dari nol."
    )

    # =========================================================================
    # SLIDE 4: ARSITEKTUR LAMBDA (WS2 -> IMPLEMENTASI WS4)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4, C_BG)
    add_header(
        s4,
        "Rancangan Arsitektur End-to-End: Lambda Architecture",
        "Menggabungkan Batch Layer (pelatihan historis akurat) dan Speed Layer (deteksi dini berlatensi rendah)",
        4,
    )

    layers = [
        ("1. DATA SOURCE & INGESTION", "Retailrocket Clickstream\n\n• Stream: Apache Kafka / Atomic File Producer\n• Batch: Apache Airflow\n• CDC: Debezium", C_WHITE),
        ("2. STORAGE & PREPROCESSING", "Data Lake & Session-ization\n\n• Ambang sesi: GAP 30 menit\n• Titik potong: addtocart pertama\n• 10 Fitur Anti-Leakage", C_WHITE),
        ("3A. BATCH LAYER (HISTORIS)", "Pelatihan & Evaluasi Berkala\n\n• Ekstraksi 20,27 juta properti\n• Training Random Forest & LR\n• Evaluasi Batch 24 Jam & 1 Jam", C_BLUE_SOFT),
        ("3B. SPEED LAYER (REAL-TIME)", "Micro-Batch Streaming (2s)\n\n• Trigger pemrosesan 2 detik\n• Inferensi RF (0,0066 ms/baris)\n• Latensi End-to-End ~1,27 detik", C_GREEN_BG),
        ("4. SERVING & INTERVENSI CRM", "Dashboard & Aksi Otomatis\n\n• Streamlit & Web Telemetry\n• Pengingat Keranjang Instan\n• Promo Voucer Tepat Sasaran", C_WHITE),
    ]
    for i, (l_title, l_body, l_bg) in enumerate(layers):
        left = 0.6 + i * 2.46
        add_card(s4, left, 1.45, 2.32, 3.3, bg_color=l_bg)
        tb = s4.shapes.add_textbox(Inches(left + 0.14), Inches(1.6), Inches(2.04), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        r0 = p0.add_run()
        r0.text = l_title
        r0.font.name = "Calibri"
        r0.font.size = Pt(12.5)
        r0.font.bold = True
        r0.font.color.rgb = C_BLUE

        p1 = tf.add_paragraph()
        p1.space_before = Pt(10)
        r1 = p1.add_run()
        r1.text = l_body
        r1.font.name = "Calibri"
        r1.font.size = Pt(12)
        r1.font.color.rgb = C_TEXT

    add_bullet_card(
        s4,
        0.6,
        4.95,
        12.133,
        2.1,
        "Mengapa Memilih Lambda Architecture & Spesifikasi Baseline Eksperimen",
        [
            ("Peran Ganda (Akurasi + Kecepatan)", "Batch Layer bertugas mengolah 20,27 juta baris properti produk dan melatih ulang model Random Forest secara periodik, sedangkan Speed Layer fokus mengeksekusi prediksi instan begitu event addtocart masuk."),
            ("Lingkungan Pengujian Terukur", "Dieksekusi secara lokal pada prosesor 12th Gen Intel Core i5-12450HX (8 Physical Cores, 12 Threads), RAM 11,78 GB, Windows 10, Python 3.11.9 (.venv) dengan total runtime pipeline 53,0 detik."),
        ],
    )

    add_notes(
        s4,
        "Poin Penjelasan Slide 4:\n"
        "- Arsitektur kami menggunakan Lambda Architecture yang membagi jalur data menjadi dua: Batch Layer dan Speed Layer.\n"
        "- Batch Layer mengurus data besar yang butuh waktu (seperti menggabungkan 20 juta baris properti item dan melatih model Random Forest).\n"
        "- Speed Layer memakai model yang sudah dilatih tadi untuk langsung menebak sesi pengguna baru dalam hitungan ~1,27 detik."
    )

    # =========================================================================
    # SLIDE 5: METODOLOGI ANTI-LEAKAGE & 10 FITUR PREDIKSI
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5, C_BG)
    add_header(
        s5,
        "Metodologi: Session-ization & Desain 10 Fitur Anti-Leakage",
        "Memastikan model hanya menggunakan informasi yang benar-benar tersedia saat barang pertama masuk keranjang",
        5,
    )

    add_bullet_card(
        s5,
        0.6,
        1.4,
        5.8,
        5.6,
        "4 Aturan Ketat Anti-Leakage pada Pipeline Kami",
        [
            ("1. Session-ization (GAP = 30 Menit)", "Sesi baru dibuat jika berganti visitorid atau tidak ada klik selama >30 menit. Sesi berlabel Abandoned (1) jika ada addtocart tapi tanpa transaction."),
            ("2. Titik Observasi Dini (First Add-to-Cart)", "Fitur hanya dihitung dari klik pertama di sesi sampai klik addtocart pertama (row <= cart_row). Semua klik setelah itu dibuang agar tidak bocor."),
            ("3. Expanding Window pada prev_sessions", "Jumlah sesi masa lalu pengunjung (prev_sessions) hanya menghitung sesi yang waktu selesainya benar-benar sebelum titik addtocart saat ini (end_ts_prev < cart_ts)."),
            ("4. Pembagian Data Kronologis (80:20 Time Split)", "Diurutkan berdasarkan waktu cart_ts: 80% awal (35.139 sesi) untuk Train, 20% akhir (8.785 sesi) untuk Test. Median harga & frekuensi kategori dihitung murni dari data Train."),
        ],
    )

    t5 = s5.shapes.add_table(11, 3, Inches(6.6), Inches(1.4), Inches(6.133), Inches(5.6))
    style_table(
        t5.table,
        ["Nama Fitur (10 Fitur)", "Kategori", "Penjelasan Singkat"],
        [
            ["prev_sessions", "Riwayat User", "Jumlah sesi masa lalu pengunjung (end_ts < cart_ts)"],
            ["elapsed_min", "Perilaku Sesi", "Durasi (menit) dari awal sesi ke addtocart pertama"],
            ["price_log", "Atribut Produk", "Logaritma harga produk ln(1 + price) dari properti 790"],
            ["cat_freq", "Atribut Produk", "Frekuensi kategori produk (categoryid) di data Train"],
            ["hour", "Konteks Waktu", "Jam terjadinya addtocart pertama (0–23 UTC)"],
            ["n_views_same_item", "Perilaku Sesi", "Berapa kali melihat produk tersebut sebelum masuk cart"],
            ["dow", "Konteks Waktu", "Hari dalam minggu (0 = Senin s.d. 6 = Minggu)"],
            ["n_events_before", "Perilaku Sesi", "Total klik di dalam sesi hingga addtocart pertama"],
            ["n_unique_items", "Perilaku Sesi", "Jumlah produk berbeda yang dilihat sebelum addtocart"],
            ["n_views_before", "Perilaku Sesi", "Total aktivitas view sebelum addtocart pertama"],
        ],
        col_widths_in=[1.85, 1.35, 2.933],
        highlight_row_idx=[0, 1, 2],
    )

    add_notes(
        s5,
        "Poin Penjelasan Slide 5:\n"
        "- Bagian paling penting di metodologi kami adalah Anti-Leakage. Di dunia nyata, kita ingin menebak tepat saat pembeli baru saja menekan tombol 'Masukkan Keranjang' pertama kali.\n"
        "- Karena itu, semua kejadian setelah tombol addtocart pertama tidak boleh dilihat oleh model. Kami mengekstrak 10 fitur yang mencakup riwayat sesi masa lalu, kecepatan klik, harga barang, kategori, dan waktu akses."
    )

    # =========================================================================
    # SLIDE 6: HASIL MODEL KLASIFIKASI & SENSITIVITAS THRESHOLD
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6, C_BG)
    add_header(
        s6,
        "Hasil Evaluasi Model Klasifikasi & Sensitivitas Threshold",
        "Perbandingan Random Forest vs. Logistic Regression pada 8.785 sesi uji kronologis (73,16% Abandoned)",
        6,
    )

    t6_top = s6.shapes.add_table(3, 9, Inches(0.6), Inches(1.4), Inches(12.133), Inches(1.45))
    style_table(
        t6_top.table,
        ["Model Klasifikasi", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC", "Balanced Acc", "Train (s)", "Inferensi / Baris"],
        [
            ["Random Forest (Utama)", "0.8175", "0.7095", "0.7597", "0.7030", "0.8574", "0.6389", "1.0011 s", "0.006635 ms"],
            ["Logistic Regression", "0.8036", "0.7487", "0.7752", "0.6829", "0.8420", "0.6250", "0.0479 s", "0.000228 ms"],
        ],
        col_widths_in=[2.3, 1.1, 1.1, 1.1, 1.1, 1.1, 1.3, 1.2, 1.833],
        highlight_row_idx=0,
    )

    t6_bot = s6.shapes.add_table(6, 6, Inches(0.6), Inches(3.15), Inches(7.1), Inches(3.85))
    style_table(
        t6_bot.table,
        ["Threshold (τ) RF", "Precision", "Recall", "F1-Score", "Bal. Acc", "Rekomendasi Strategi CRM"],
        [
            ["τ = 0.30", "0.7551", "0.9818", "0.8536", "0.5568", "Badge pengingat gratis ongkir di UI"],
            ["τ = 0.40", "0.7751", "0.9136", "0.8387", "0.5955", "Push notification / pesan chat otomatis"],
            ["τ = 0.50 (Default)", "0.8175", "0.7095", "0.7597", "0.6389", "Keseimbangan optimal (Balanced Acc tertinggi)"],
            ["τ = 0.60", "0.8771", "0.4176", "0.5658", "0.6291", "Voucer diskon 5%–10% (hemat budget promo)"],
            ["τ = 0.70", "0.9055", "0.2533", "0.3959", "0.5906", "Subsidi diskon besar khusus risiko sangat tinggi"],
        ],
        col_widths_in=[1.4, 0.9, 0.9, 0.9, 0.9, 2.1],
        highlight_row_idx=2,
    )

    add_bullet_card(
        s6,
        7.95,
        3.15,
        4.783,
        3.85,
        "Insight Kunci Performa Model",
        [
            ("Unggul di PR-AUC (0,8574)", "Karena data uji didominasi kelas Abandoned (73,16%), metrik PR-AUC lebih jujur dibanding ROC-AUC. Random Forest unggul di Precision, ROC-AUC, PR-AUC, dan Balanced Accuracy."),
            ("Sangat Cepat untuk Streaming", "Waktu inferensi Random Forest hanya 0,0066 ms per baris (~150.000 prediksi/detik), sehingga sangat ringan dijalankan secara real-time."),
            ("Fleksibilitas Threshold (τ)", "Toko online bisa mengatur ambang τ: pakai τ=0,40 untuk pengingat gratis (Recall 91,4%), atau τ=0,60 untuk kupon diskon agar tidak salah kasih promo (Precision 87,7%)."),
        ],
    )

    add_notes(
        s6,
        "Poin Penjelasan Slide 6:\n"
        "- Random Forest mengungguli Logistic Regression di hampir semua metrik utama: Precision 81,75%, ROC-AUC 0,7030, PR-AUC 0,8574, dan Balanced Accuracy 0,6389.\n"
        "- Menariknya, walaupun Random Forest terdiri dari 200 pohon, waktu tebakannya hanya 0,0066 milidetik per baris, artinya 1 detik bisa menebak 150 ribu sesi.\n"
        "- Kami juga menguji pergeseran threshold dari 0,3 sampai 0,7 agar tim marketing bisa menyesuaikan antara pengingat gratis vs pemberian kupon diskon."
    )

    # =========================================================================
    # SLIDE 7: FAKTOR PENYEBAB UTAMA (FEATURE IMPORTANCE) & POLA WAKTU
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7, C_BG)
    add_header(
        s7,
        "Faktor Penyebab Cart Abandonment & Pola Waktu Belanja",
        "Apa yang membedakan pembeli serius vs. pengunjung yang meninggalkan keranjang?",
        7,
    )

    fig1_path = os.path.join(FIG_DIR, "fig1_feature_importance.png")
    add_card(s7, 0.6, 1.4, 6.2, 3.6)
    s7.shapes.add_picture(fig1_path, Inches(0.7), Inches(1.48), width=Inches(6.0))

    fig2_path = os.path.join(FIG_DIR, "fig2_temporal_patterns.png")
    add_card(s7, 6.95, 1.4, 5.78, 3.6)
    s7.shapes.add_picture(fig2_path, Inches(7.05), Inches(1.65), width=Inches(5.58))

    add_bullet_card(
        s7,
        0.6,
        5.15,
        12.133,
        1.9,
        "Temuan Utama Perilaku Konsumen dari Data Retailrocket",
        [
            ("1. Pengunjung Baru Jauh Lebih Rawan Batal (prev_sessions = 0,1995)", "Pembeli yang tuntas membayar rata-rata punya 9,44 sesi masa lalu, sedangkan yang meninggalkan keranjang rata-rata hanya punya 2,20 sesi."),
            ("2. Fenomena 'Keranjang sebagai Bookmark' (elapsed_min = 0,1600 & price_log = 0,1515)", "Pelaku abandonment memasukkan barang ke keranjang lebih cepat (4,26 menit vs 8,89 menit pada pembeli) dan sensitif pada barang berharga tinggi."),
            ("3. Jam & Hari Paling Rawan (hour = 0,1016)", "Tingkat batal checkout tertinggi terjadi pukul 09:00–12:00 UTC (85,84%) dan pada Akhir Pekan (Sabtu 77,39% & Minggu 76,55%), sedangkan konversi terbaik terjadi sore hari pukul 15:00 UTC."),
        ],
    )

    add_notes(
        s7,
        "Poin Penjelasan Slide 7:\n"
        "- Dari grafik Feature Importance di kiri, 3 faktor terkuat penyebab orang batal checkout adalah: (1) riwayat kunjungan sebelumnya (prev_sessions), (2) durasi waktu sampai masuk keranjang (elapsed_min), dan (3) harga barang (price_log).\n"
        "- Dari grafik pola waktu di kanan, orang paling sering meninggalkan keranjang saat jam pagi-siang (85,8%) dan saat akhir pekan Sabtu-Minggu (77,4%) karena sifatnya window shopping."
    )

    # =========================================================================
    # SLIDE 8: INTI EKSPERIMEN BIG DATA — BATCH VS NEAR REAL-TIME
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8, C_BG)
    add_header(
        s8,
        "Perbandingan Batch vs. Near Real-Time (Effective Recall)",
        "Bukti kuantitatif: model akurat menjadi percuma jika pemrosesan datanya terlambat melewati batas sesi",
        8,
    )

    fig3_path = os.path.join(FIG_DIR, "fig3_latency_effective_recall.png")
    add_card(s8, 0.6, 1.4, 5.85, 3.65)
    s8.shapes.add_picture(fig3_path, Inches(0.72), Inches(1.5), width=Inches(5.6))

    t8 = s8.shapes.add_table(6, 5, Inches(6.6), Inches(1.4), Inches(6.133), Inches(3.65))
    style_table(
        t8.table,
        ["Skenario Jendela", "Mean Latency", "Tepat Waktu (%)", "TP Terselamatkan", "Effective Recall"],
        [
            ["Batch Harian (24 Jam)", "37.343,6 s (~10,4 jam)", "3.60%", "113 / 6.427", "0.0176 (1,8%)"],
            ["Batch Per Jam (1 Jam)", "1.792,3 s (~29,9 mnt)", "60.47%", "2.512 / 6.427", "0.3909 (39,1%)"],
            ["Micro-Batch (5 Menit)", "150,2 s (~2,5 mnt)", "100.00%", "4.560 / 6.427", "0.7095 (71,0%)"],
            ["Near Real-Time (1 Menit)", "30,5 detik", "100.00%", "4.560 / 6.427", "0.7095 (71,0%)"],
            ["Near Real-Time (10 Detik)", "5,5 detik", "100.00%", "4.560 / 6.427", "0.7095 (71,0%)"],
        ],
        col_widths_in=[1.65, 1.35, 1.0, 1.05, 1.083],
        highlight_row_idx=[2, 3, 4],
    )

    add_bullet_card(
        s8,
        0.6,
        5.2,
        12.133,
        1.85,
        "Rumus Effective Recall = TP_terdeteksi_sebelum_deadline / Total_Aktual_Abandoned (Deadline = akhir sesi + 30 menit)",
        [
            ("Batch Harian Kehilangan 97,5% Peluang", "Dari 4.560 pembeli batal checkout yang berhasil ditebak model, Batch Harian hanya sempat menangkap 113 sesi tepat waktu (Effective Recall anjlok dari 70,95% ke 1,76%)."),
            ("Batch Per Jam Kehilangan Hampir Separuh Peluang", "Dengan jeda 1 jam, 39,5% pengunjung sudah pergi sebelum jadwal batch jalan, sehingga Effective Recall turun menjadi 39,09% (2.512 sesi)."),
            ("Micro-Batch (≤5 Menit) & Streaming Menyelamatkan 100% Prediksi", "Begitu jendela diperkecil ke 5 menit, 1 menit, atau 10 detik, seluruh 4.560 prediksi keluar sebelum batas waktu (Effective Recall utuh 70,95% — naik 40,3 kali lipat dibanding Batch Harian)."),
        ],
    )

    add_notes(
        s8,
        "Poin Penjelasan Slide 8 (Slide Paling Penting):\n"
        "- Ini adalah jawaban dari pertanyaan utama proyek kami: seberapa besar pengaruh kecepatan deteksi?\n"
        "- Kami memakai model Random Forest yang persis sama (kemampuan tebaknya 70,95% / 4.560 kasus). Tapi ketika dijalankan pada Batch Harian (24 jam), 96,4% pembeli sudah keburu pergi, sehingga yang benar-benar bisa dibujuk tinggal 113 orang (Effective Recall cuma 1,76%).\n"
        "- Kalau pakai Batch Per Jam, kita masih kehilangan hampir separuh pembeli (Effective Recall 39,09%).\n"
        "- Tapi begitu kita pindah ke Micro-Batch (5 menit) atau Near Real-Time (1 menit / 10 detik), 100% tebakan keluar sebelum pembeli pergi, sehingga Effective Recall utuh di 70,95%."
    )

    # =========================================================================
    # SLIDE 9: HASIL BENCHMARK STREAMING NYATA & DASHBOARD OPERASIONAL
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9, C_BG)
    add_header(
        s9,
        "Uji Micro-Batch Streaming (Speed Layer) & Dashboard Telemetry",
        "Simulasi aliran data real-time dengan atomic file rename & trigger 2 detik",
        9,
    )

    add_kpi_box(s9, 0.6, 1.4, 2.85, 1.35, "MEAN STREAMING LATENCY", "1.2735 s", "Dari data ditulis s.d. selesai ditebak", C_GREEN, C_GREEN_BG)
    add_kpi_box(s9, 3.69, 1.4, 2.85, 1.35, "MEDIAN (P50) LATENCY", "1.2596 s", "50% sesi selesai dalam ≤1,26 detik", C_BLUE, C_BLUE_SOFT)
    add_kpi_box(s9, 6.78, 1.4, 2.85, 1.35, "RENTANG MIN / MAX", "0.50s – 2.08s", "Konsisten di bawah batas 2,1 detik")
    add_kpi_box(s9, 9.87, 1.4, 2.86, 1.35, "INFERENSI RF PER BATCH", "28.98 ms", "Untuk ratusan baris per micro-batch")

    add_bullet_card(
        s9,
        0.6,
        2.95,
        5.9,
        4.1,
        "Cara Kerja Simulasi Streaming (Step 8)",
        [
            ("Producer Thread (Aliran Data Masuk)", "Mengirimkan 1.000 sesi uji secara bertahap dalam 10 berkas chunk CSV (@100 baris) menggunakan atomic file rename (os.replace) agar engine tidak membaca file setengah jadi."),
            ("Consumer Micro-Batch (Trigger 2 Detik)", "Memeriksa chunk baru setiap 2 detik, memuat fitur, dan menjalankan prediksi probabilitas Random Forest."),
            ("Hasil Pengukuran End-to-End", "Rata-rata total waktu tunggu dari event masuk sampai skor risiko keluar hanya 1,2735 detik—jauh lebih cepat dibanding median sisa waktu user di web (85 detik)."),
        ],
    )

    add_bullet_card(
        s9,
        6.83,
        2.95,
        5.9,
        4.1,
        "Implementasi Dashboard Operasional (Streamlit & Web)",
        [
            ("1. Simulator Jendela Arsitektur", "Memungkinkan tim melihat langsung perubahan Effective Recall saat beralih dari Batch 24 jam ke Near Real-Time 10 detik."),
            ("2. Simulator Threshold (τ) Interaktif", "Memilih batas probabilitas (0,30 s.d. 0,70) sesuai jenis intervensi (pengingat gratis vs voucer diskon)."),
            ("3. Live Session Scoring Feed", "Menampilkan tabel aliran sesi yang baru masuk beserta skor probabilitas Random Forest dan rekomendasi aksi CRM secara langsung."),
        ],
    )

    add_notes(
        s9,
        "Poin Penjelasan Slide 9:\n"
        "- Selain simulasi rumus, kami juga menguji aliran data streaming nyata sebanyak 1.000 sesi dengan trigger 2 detik.\n"
        "- Hasilnya, rata-rata waktu dari data masuk sampai model selesai menebak hanya 1,27 detik (maksimal 2,07 detik).\n"
        "- Hasil ini juga sudah kami pasang ke dalam Dashboard interaktif (baik versi Streamlit maupun HTML) yang bisa dipakai tim CRM memantau sesi berisiko."
    )

    # =========================================================================
    # SLIDE 10: KETERBATASAN PENELITIAN (STUDY LIMITATIONS)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10, C_BG)
    add_header(
        s10,
        "Diskusi & Keterbatasan Metodologis (Study Limitations)",
        "Transparansi ilmiah sesuai standar publikasi jurnal SINTA 4 (INISTA / JICT)",
        10,
    )

    add_bullet_card(
        s10,
        0.6,
        1.45,
        5.9,
        5.55,
        "4 Keterbatasan Eksperimen yang Dicatat Secara Eksplisit",
        [
            ("1. Asumsi Batas Waktu Intervensi (Deadline 30 Menit)", "Batas waktu intervensi efektif (akhir sesi + 30 menit) merupakan asumsi analitis yang diturunkan dari ambang inaktivitas sesi. Di dunia nyata, pop-up dalam aplikasi butuh respons dalam hitungan detik saat user masih aktif di layar."),
            ("2. Resolusi Waktu Atribut Produk (item_properties)", "Harga (properti 790) dan kategori diambil dari nilai terakhir yang tercatat per itemid untuk efisiensi pemrosesan 20,27 juta baris, bukan nilai historis per milidetik event."),
            ("3. Cakupan Satu Dataset & Satu Periode", "Eksperimen menggunakan satu dataset ritel daring (Retailrocket) selama 4,5 bulan dengan ID dan nilai harga yang telah di-hash/ditransformasi."),
            ("4. Simulasi Streaming Berbasis File Lokal", "Pengujian streaming dilakukan menggunakan mekanisme atomic file-based micro-batching pada satu node komputasi lokal, belum menggunakan klaster multi-broker Apache Kafka produksi."),
        ],
    )

    add_bullet_card(
        s10,
        6.83,
        1.45,
        5.9,
        5.55,
        "Rekomendasi Praktis untuk Platform E-Commerce",
        [
            ("Gunakan Arsitektur Hibrida (Lambda)", "Tetap gunakan pemrosesan Batch harian/mingguan untuk melatih ulang model Random Forest pada data historis, tetapi wajib gunakan Speed Layer (micro-batch ≤1–5 menit atau streaming 2 detik) untuk inferensi skor risiko."),
            ("Personalisasi Intervensi Berdasarkan Riwayat & Waktu", "Fokuskan promo retensi pada pengunjung baru (prev_sessions = 0) yang memasukkan barang berharga tinggi secara cepat di jam rawan (09:00–12:00 UTC dan akhir pekan)."),
            ("Pisahkan Strategi Berdasarkan Threshold (τ)", "Gunakan τ = 0,40 untuk intervensi tanpa biaya (pop-up pengingat stok/gratis ongkir) dan τ = 0,60 untuk pemberian kupon diskon agar margin keuntungan terjaga."),
        ],
    )

    add_notes(
        s10,
        "Poin Penjelasan Slide 10:\n"
        "- Sesuai kaidah penulisan jurnal ilmiah, kami mencatat 4 keterbatasan penelitian secara jujur: asumsi deadline 30 menit, pengambilan nilai terakhir pada atribut produk, cakupan 1 dataset, serta pengujian streaming pada 1 mesin lokal.\n"
        "- Di sisi kanan adalah rekomendasi konkret bagaimana toko online menerapkan sistem ini di produksi."
    )

    # =========================================================================
    # SLIDE 11: KESIMPULAN
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11, C_NAVY)

    strip11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    strip11.fill.solid()
    strip11.fill.fore_color.rgb = RGBColor(56, 189, 248)
    strip11.line.fill.background()

    tb11 = s11.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(1.2))
    tf11 = tb11.text_frame
    p11_0 = tf11.paragraphs[0]
    r11_0 = p11_0.add_run()
    r11_0.text = "KESIMPULAN AKHIR — KELOMPOK 15"
    r11_0.font.name = "Consolas"
    r11_0.font.size = Pt(13)
    r11_0.font.bold = True
    r11_0.font.color.rgb = RGBColor(56, 189, 248)

    p11_1 = tf11.add_paragraph()
    p11_1.space_before = Pt(6)
    r11_1 = p11_1.add_run()
    r11_1.text = "Deteksi Dini + Pemrosesan Near Real-Time = Peluang Intervensi 40,3× Lebih Tinggi"
    r11_1.font.name = "Calibri"
    r11_1.font.size = Pt(28)
    r11_1.font.bold = True
    r11_1.font.color.rgb = C_WHITE

    conclusions = [
        ("1. Prediksi Dini yang Akurat & Bebas Bocor Data", "Pada titik addtocart pertama, Random Forest mencapai Precision 0,8175, ROC-AUC 0,7030, PR-AUC 0,8574, dan Balanced Accuracy 0,6389 dengan kecepatan tebak 0,0066 ms/baris."),
        ("2. Faktor Penentu Utama Batal Checkout", "Riwayat sesi sebelumnya (prev_sessions = 0,1995), durasi menuju keranjang (elapsed_min = 0,1600), dan harga barang (price_log = 0,1515) menyumbang >51% daya prediksi model."),
        ("3. Bukti Nyata Keunggulan Streaming vs. Batch", "Batch Harian (24 jam) menjatuhkan Effective Recall ke 0,0176 (hanya 3,6% tepat waktu) dan Batch 1 Jam ke 0,3909. Sebaliknya, Micro-Batch (≤5 menit) dan Streaming (latensi rata-rata 1,27 detik) mempertahankan Effective Recall penuh 0,7095 (100% tepat waktu)."),
    ]
    for i, (c_title, c_desc) in enumerate(conclusions):
        top = 2.05 + i * 1.45
        card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top), Inches(11.733), Inches(1.25))
        card.adjustments[0] = 0.03
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(30, 41, 59)
        card.line.color.rgb = RGBColor(71, 85, 105)

        ctb = s11.shapes.add_textbox(Inches(1.05), Inches(top + 0.16), Inches(11.2), Inches(0.95))
        ctf = ctb.text_frame
        ctf.word_wrap = True
        cp0 = ctf.paragraphs[0]
        cr0 = cp0.add_run()
        cr0.text = c_title
        cr0.font.name = "Calibri"
        cr0.font.size = Pt(16)
        cr0.font.bold = True
        cr0.font.color.rgb = RGBColor(56, 189, 248)

        cp1 = ctf.add_paragraph()
        cp1.space_before = Pt(4)
        cr1 = cp1.add_run()
        cr1.text = c_desc
        cr1.font.name = "Calibri"
        cr1.font.size = Pt(13.5)
        cr1.font.color.rgb = C_WHITE

    tb_end = s11.shapes.add_textbox(Inches(0.8), Inches(6.55), Inches(11.733), Inches(0.5))
    tf_end = tb_end.text_frame
    p_end = tf_end.paragraphs[0]
    p_end.alignment = PP_ALIGN.CENTER
    r_end = p_end.add_run()
    r_end.text = "Terima Kasih — Kelompok 15 (Arief Adhitya Ramadhan · Muhammad Bafqi · Zidan Dzulqarnain)"
    r_end.font.name = "Calibri"
    r_end.font.size = Pt(15)
    r_end.font.bold = True
    r_end.font.color.rgb = RGBColor(203, 213, 225)

    add_notes(
        s11,
        "Penutup Presentasi:\n"
        "- Sebagai penutup, proyek kami membuktikan bahwa menebak pembeli yang mau batal checkout sejak klik keranjang pertama itu sangat bisa dilakukan dengan PR-AUC 0,8574.\n"
        "- Namun tebakan itu hanya berguna kalau diproses secara cepat (Micro-Batch atau Near Real-Time Streaming dengan latensi ~1,27 detik), yang meningkatkan peluang penyelamatan transaksi hingga 40,3 kali lipat dibanding Batch Harian. Terima kasih, silakan jika ada pertanyaan."
    )

    prs.save(OUT_PPTX)
    print(f"Successfully generated presentation: {OUT_PPTX}")


if __name__ == "__main__":
    build_presentation()
