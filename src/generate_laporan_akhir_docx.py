# -*- coding: utf-8 -*-
"""
Generate Laporan Akhir Proyek Mata Kuliah Teknologi Big Data (.docx)
strictly following 'Template Laporan Akhir Teknologi Big Data 2026.docx':
- Kertas A4 (21.0 cm x 29.7 cm)
- Font Times New Roman 12 pt, Spasi 1,15
- 5-8 halaman isi utama (BAB I s.d. BAB IV), di luar halaman judul, daftar pustaka, dan lampiran.
"""

import os
import docx
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

BASE_DIR = r"c:\Bafqi\Big Data"
FIG_DIR = os.path.join(BASE_DIR, "outputs", "figures")
OUT_DOCX = os.path.join(BASE_DIR, "Laporan_Akhir_Proyek_Teknologi_Big_Data_Kelompok_15.docx")


def create_pipeline_diagram(out_path):
    """Create a clean, high-resolution (300 DPI) flowchart diagram of the data processing pipeline."""
    fig, ax = plt.subplots(figsize=(10.0, 4.4), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    boxes = [
        (0.25, 2.65, 2.1, 1.35, "1. Akuisisi Data\n(Retailrocket CSV)\n• events (2,75 juta)\n• item_properties (20,27 juta)\n• category_tree (1.669)"),
        (2.8, 2.65, 2.1, 1.35, "2. Session-ization &\nPelabelan Target\n• Urut visitorid & ts\n• Jeda > 30 menit\n• Filter sesi addtocart\n  (43.924 sesi)"),
        (5.35, 2.65, 2.2, 1.35, "3. Ekstraksi 10 Fitur\n(Anti-Leakage)\n• Titik potong: addtocart\n  pertama (cart_ts)\n• Strict prev_sessions\n• Split kronologis 80:20"),
        (8.0, 2.65, 2.2, 1.35, "4. Pemodelan ML\n(Class Balanced)\n• Random Forest\n• Logistic Regression\n• Evaluasi & Feature\n  Importance"),
        (0.4, 0.4, 3.0, 1.4, "5a. Batch Layer\n(Pemrosesan Berkala)\n• Jendela Harian (86.400 dtk)\n• Jendela Per Jam (3.600 dtk)\n• Evaluasi Effective Recall"),
        (3.85, 0.4, 3.15, 1.4, "5b. Speed Layer Streaming\n(Near Real-Time / PySpark)\n• Jendela NRT (300s, 60s, 10s)\n• Spark Structured Streaming\n  (Trigger 2 dtk, foreachBatch RF)"),
        (7.45, 0.4, 2.75, 1.4, "6. Serving Layer\n(Interactive Dashboard)\n• Streamlit (dashboard.py)\n• Web UI (dashboard.html)\n• Simulator Threshold (τ)\n  & Live Stream CRM"),
    ]

    for x, y, w, h, text in boxes:
        is_serving = text.startswith("6.")
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.08,rounding_size=0.12",
            ec="#0f4c81" if is_serving else "#1e293b",
            fc="#f0f9ff" if is_serving else "#f8fafc",
            lw=1.5 if is_serving else 1.4
        )
        ax.add_patch(rect)
        lines = text.split("\n")
        title = "\n".join(lines[:2])
        body = "\n".join(lines[2:])
        ax.text(x + w / 2, y + h - 0.30, title, ha="center", va="center",
                fontsize=8.3, fontweight="bold", family="sans-serif", color="#0f172a")
        ax.text(x + 0.12, y + 0.44, body, ha="left", va="center",
                fontsize=7.4, family="sans-serif", color="#334155")

    arrow_style = dict(arrowstyle="-|>,head_width=0.25,head_length=0.4", lw=1.4, color="#1e293b")
    # Horizontal arrows top row
    ax.annotate("", xy=(2.72, 3.32), xytext=(2.42, 3.32), arrowprops=arrow_style)
    ax.annotate("", xy=(5.27, 3.32), xytext=(4.97, 3.32), arrowprops=arrow_style)
    ax.annotate("", xy=(7.92, 3.32), xytext=(7.62, 3.32), arrowprops=arrow_style)
    # Clean orthogonal-style routing from step 4 to 5a and 5b via the middle corridor (y = 2.22)
    ax.plot([9.1, 9.1, 1.9], [2.65, 2.22, 2.22], color="#1e293b", lw=1.3)
    ax.annotate("", xy=(1.9, 1.82), xytext=(1.9, 2.22), arrowprops=arrow_style)
    ax.annotate("", xy=(5.42, 1.82), xytext=(5.42, 2.22), arrowprops=arrow_style)
    # Arrow from 5b to 6 (Serving Layer)
    ax.annotate("", xy=(7.38, 1.10), xytext=(7.06, 1.10), arrowprops=arrow_style)

    ax.set_title("Diagram Alur Pengolahan Data dan Evaluasi Arsitektur (Lambda Architecture + Serving Dashboard)",
                 fontsize=10, fontweight="bold", pad=6, color="#0f172a")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def create_dashboard_tab1_figure(out_path):
    """Render high-resolution (300 DPI) figure of the Operational Telemetry Dashboard (Tab 1: Batch vs NRT & Live Stream)."""
    fig, ax = plt.subplots(figsize=(11.0, 6.3), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.3)
    ax.axis("off")

    # Background canvas
    ax.add_patch(mpatches.Rectangle((0, 0), 11, 6.3, fc="#f8fafc", ec="#cbd5e1", lw=1.5))

    # Top operational bar
    ax.add_patch(mpatches.Rectangle((0, 5.78), 11, 0.52, fc="#ffffff", ec="#e2e8f0", lw=1.0))
    ax.text(0.22, 6.08, "Early Cart Abandonment Telemetry & Architecture Simulator",
            fontsize=10.5, fontweight="bold", color="#0f172a")
    ax.text(0.22, 5.88, "Kelompok 15 · Retailrocket Clickstream (2.756.101 Events · 43.924 Cart Sessions) · Baseline CPU: i5-12450HX · 11.78 GB RAM",
            fontsize=7.2, color="#64748b", family="monospace")
    # Status pill
    ax.add_patch(mpatches.FancyBboxPatch((8.55, 5.88), 2.25, 0.30, boxstyle="round,pad=0.04,rounding_size=0.08",
                                         fc="#ecfdf5", ec="#a7f3d0", lw=1.0))
    ax.text(9.67, 6.03, "● Speed Layer: 1.27s Mean Latency", ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="#047857")

    # Navigation Tabs bar
    ax.add_patch(mpatches.Rectangle((0, 5.38), 11, 0.40, fc="#ffffff", ec="#e2e8f0", lw=1.0))
    ax.add_patch(mpatches.Rectangle((0.20, 5.38), 3.45, 0.04, fc="#0f4c81", ec="none"))
    ax.text(0.25, 5.57, "1. Batch vs. Near Real-Time & Live Stream", fontsize=8.0, fontweight="bold", color="#0f4c81")
    ax.text(3.95, 5.57, "2. Model Performance & Threshold Simulator", fontsize=8.0, color="#64748b")
    ax.text(7.55, 5.57, "3. Feature Drivers & Temporal Behavior", fontsize=8.0, color="#64748b")

    # Global 6-Card Telemetry Strip
    kpis = [
        ("TOTAL CLICKSTREAM EVENTS", "2,756,101", "1,761,660 total sessions", "#0f172a"),
        ("CART SESSIONS (TARGET)", "43,924", "Train: 35,139 · Test: 8,785", "#0f172a"),
        ("CART ABANDONMENT RATE", "72.83%", "31,992 abandoned vs 11,932", "#b91c1c"),
        ("RANDOM FOREST PR-AUC", "0.8574", "ROC-AUC: 0.7030 · Prec: 0.8175", "#0f4c81"),
        ("MEDIAN REMAINING SESSION", "85.0 s", "Mean: 551.7 s after addtocart", "#0f172a"),
        ("EFFECTIVE RECALL GAIN", "40.3×", "0.7095 (NRT) vs 0.0176 (Daily)", "#047857"),
    ]
    card_w = (10.6 - 5 * 0.10) / 6.0
    for idx, (lbl, val, sub, col) in enumerate(kpis):
        cx = 0.20 + idx * (card_w + 0.10)
        ax.add_patch(mpatches.FancyBboxPatch((cx, 4.48), card_w, 0.78, boxstyle="round,pad=0.02,rounding_size=0.05",
                                             fc="#ffffff", ec="#e2e8f0", lw=1.0))
        ax.text(cx + 0.08, 5.12, lbl, fontsize=5.8, fontweight="bold", color="#64748b")
        ax.text(cx + 0.08, 4.82, val, fontsize=11.0, fontweight="bold", color=col, family="monospace")
        ax.text(cx + 0.08, 4.58, sub, fontsize=5.8, color="#64748b")

    # Left Panel: Architectural Processing Window vs Effective Recall
    ax.add_patch(mpatches.FancyBboxPatch((0.20, 0.18), 5.65, 4.16, boxstyle="round,pad=0.02,rounding_size=0.06",
                                         fc="#ffffff", ec="#cbd5e1", lw=1.0))
    ax.text(0.35, 4.12, "Architectural Processing Window vs. Effective Recall", fontsize=8.8, fontweight="bold", color="#0f172a")
    ax.text(0.35, 3.94, "Impact of scheduling latency on timely CRM intervention (Deadline = t_end + 30 min)", fontsize=6.8, color="#64748b")

    # Mini chart box inside Left Panel
    ax.add_patch(mpatches.Rectangle((0.35, 2.15), 5.35, 1.68, fc="#f8fafc", ec="#e2e8f0", lw=0.8))
    xs = [0.85, 1.95, 3.05, 4.15, 5.20]
    er_y = [2.32, 2.82, 3.25, 3.25, 3.25]
    dl_y = [2.35, 3.10, 3.62, 3.62, 3.62]
    ax.plot(xs, dl_y, linestyle="--", color="#64748b", lw=1.4, marker="s", markersize=4, label="Decided < Deadline (%)")
    ax.plot(xs, er_y, linestyle="-", color="#0f4c81", lw=2.0, marker="o", markersize=5, label="Effective Recall (%)")
    for idx_pt, (x_i, y_i, txt, c_i) in enumerate(zip(xs, er_y, ["1.8%", "39.1%", "71.0%", "71.0%", "71.0%"],
                                  ["#b91c1c", "#b45309", "#047857", "#047857", "#047857"])):
        dy = -0.17 if idx_pt == 1 else (0.12 if idx_pt == 0 else -0.17)
        dx = -0.18 if idx_pt == 0 else 0.0
        ax.text(x_i + dx, y_i + dy, txt, ha="center", fontsize=6.5, fontweight="bold", color=c_i, family="monospace")
    for x_i, lbl in zip(xs, ["Daily (24h)", "Hourly (1h)", "Micro (5m)", "NRT (1m)", "NRT (10s)"]):
        ax.text(x_i, 2.20, lbl, ha="center", fontsize=6.2, fontweight="bold", color="#334155")
    ax.text(0.45, 3.68, "── Effective Recall (%)    - - Decided Before Deadline (%)", fontsize=6.3, fontweight="bold", color="#0f4c81")

    # Table inside Left Panel
    headers_l = ["Processing Mode", "Win (s)", "Mean Lat", "Before DL", "Timely TP", "Eff. Recall"]
    rows_l = [
        ["Batch Harian (24 Jam)", "86,400", "37,343.6s", "3.60%", "113/6,427", "0.0176"],
        ["Batch Per Jam (1 Jam)", "3,600", "1,792.3s", "60.47%", "2,512/6,427", "0.3909"],
        ["Micro-Batch (5 Menit)", "300", "150.2s", "100.0%", "4,560/6,427", "0.7095"],
        ["Near Real-Time (1 Menit)", "60", "30.5s", "100.0%", "4,560/6,427", "0.7095"],
        ["Near Real-Time (10 Detik)", "10", "5.5s", "100.0%", "4,560/6,427", "0.7095"],
    ]
    col_x_l = [0.38, 2.15, 2.78, 3.55, 4.25, 5.05]
    ax.add_patch(mpatches.Rectangle((0.35, 1.82), 5.35, 0.25, fc="#f1f5f9", ec="#cbd5e1", lw=0.6))
    for cx, h_txt in zip(col_x_l, headers_l):
        ax.text(cx, 1.91, h_txt, fontsize=6.2, fontweight="bold", color="#334155")
    for r_idx, r_vals in enumerate(rows_l):
        ry = 1.54 - r_idx * 0.27
        bg = "#e0f2fe" if r_idx == 2 else "#ffffff"
        ax.add_patch(mpatches.Rectangle((0.35, ry), 5.35, 0.27, fc=bg, ec="#e2e8f0", lw=0.5))
        for c_idx, (cx, val) in enumerate(zip(col_x_l, r_vals)):
            col_txt = "#047857" if (c_idx == 5 and r_idx >= 2) else ("#b91c1c" if (c_idx == 5 and r_idx == 0) else "#0f172a")
            fw = "bold" if (c_idx == 5 or r_idx == 2) else "normal"
            ax.text(cx, ry + 0.09, val, fontsize=6.1, fontweight=fw, color=col_txt)

    # Right Panel: Speed Layer Micro-Batch Telemetry (2s Trigger)
    ax.add_patch(mpatches.FancyBboxPatch((6.00, 0.18), 4.80, 4.16, boxstyle="round,pad=0.02,rounding_size=0.06",
                                         fc="#ffffff", ec="#cbd5e1", lw=1.0))
    ax.text(6.15, 4.12, "Speed Layer Micro-Batch Telemetry (2s Trigger)", fontsize=8.8, fontweight="bold", color="#0f172a")
    ax.text(6.15, 3.94, "Atomic file-based streaming benchmark & real-time session scoring", fontsize=6.8, color="#64748b")

    # 2 Metric cards in Right Panel
    ax.add_patch(mpatches.FancyBboxPatch((6.15, 3.18), 2.20, 0.64, boxstyle="round,pad=0.02,rounding_size=0.04",
                                         fc="#f8fafc", ec="#e2e8f0", lw=0.8))
    ax.text(6.25, 3.66, "Mean End-to-End Latency", fontsize=6.2, fontweight="bold", color="#64748b")
    ax.text(6.25, 3.40, "1.2735 s", fontsize=10.5, fontweight="bold", color="#0f4c81", family="monospace")
    ax.text(6.25, 3.24, "Median (P50): 1.2596 s", fontsize=5.8, color="#64748b")

    ax.add_patch(mpatches.FancyBboxPatch((8.45, 3.18), 2.20, 0.64, boxstyle="round,pad=0.02,rounding_size=0.04",
                                         fc="#f8fafc", ec="#e2e8f0", lw=0.8))
    ax.text(8.55, 3.66, "Min / Max Stream Latency", fontsize=6.2, fontweight="bold", color="#64748b")
    ax.text(8.55, 3.40, "0.498s / 2.077s", fontsize=10.0, fontweight="bold", color="#0f172a", family="monospace")
    ax.text(8.55, 3.24, "Batch RF Inference: 28.98 ms", fontsize=5.8, color="#64748b")

    ax.text(6.15, 2.94, "Live Session Scoring Replay (Test Set Stream · 2.0s Micro-Batch Trigger)",
            fontsize=6.8, fontweight="bold", color="#0f172a")

    headers_r = ["Session ID", "Prev", "Elap", "RF Prob", "CRM Action", "Lat"]
    rows_r = [
        ["S-1749241 (B#6)", "0", "0.3m", "0.89", "Offer 5% Flash Coupon", "1.45s", True],
        ["S-1749234 (B#5)", "8", "6.5m", "0.31", "No Interrupt (Organic)", "1.09s", False],
        ["S-1749229 (B#4)", "1", "2.1m", "0.68", "Offer 5% Flash Coupon", "1.38s", True],
        ["S-1749215 (B#3)", "0", "1.4m", "0.79", "Trigger Cart Reminder", "0.92s", True],
        ["S-1749208 (B#2)", "14", "11.2m", "0.22", "No Interrupt (Organic)", "1.21s", False],
        ["S-1749201 (B#1)", "0", "0.8m", "0.84", "Send Free-Ship Prompt", "1.14s", True],
    ]
    col_x_r = [6.18, 7.22, 7.62, 8.08, 8.62, 10.22]
    ax.add_patch(mpatches.Rectangle((6.15, 2.60), 4.50, 0.25, fc="#f1f5f9", ec="#cbd5e1", lw=0.6))
    for cx, h_txt in zip(col_x_r, headers_r):
        ax.text(cx, 2.69, h_txt, fontsize=6.1, fontweight="bold", color="#334155")
    for r_idx, r_vals in enumerate(rows_r):
        ry = 2.33 - r_idx * 0.27
        ax.add_patch(mpatches.Rectangle((6.15, ry), 4.50, 0.27, fc="#ffffff", ec="#e2e8f0", lw=0.5))
        is_risk = r_vals[6]
        for c_idx, (cx, val) in enumerate(zip(col_x_r, r_vals[:6])):
            col_txt = "#b91c1c" if (c_idx == 3 and is_risk) else ("#047857" if (c_idx == 3 and not is_risk) else "#0f172a")
            fw = "bold" if c_idx in (0, 3) else "normal"
            ax.text(cx, ry + 0.09, val, fontsize=6.0, fontweight=fw, color=col_txt)

    ax.text(6.15, 0.42, "Note: Under a 2-second micro-batch trigger, 100% of predicted abandonments are\nflagged within ~1.27s of first addtocart (well inside the 85.0s median window).",
            fontsize=6.1, style="italic", color="#475569")

    plt.tight_layout(pad=0.1)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def create_dashboard_tab23_figure(out_path):
    """Render high-resolution (300 DPI) figure of Dashboard Tab 2 (Threshold Simulator & Confusion Matrix) and Tab 3 (Feature & Temporal)."""
    fig, ax = plt.subplots(figsize=(11.0, 5.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    ax.add_patch(mpatches.Rectangle((0, 0), 11, 5.2, fc="#f8fafc", ec="#cbd5e1", lw=1.5))

    # Left Card: Tab 2 Interactive Decision Threshold Simulator & Confusion Matrix
    ax.add_patch(mpatches.FancyBboxPatch((0.20, 0.20), 5.25, 4.80, boxstyle="round,pad=0.02,rounding_size=0.06",
                                         fc="#ffffff", ec="#cbd5e1", lw=1.0))
    ax.text(0.35, 4.74, "Tab 2: Interactive Decision Threshold (τ) Simulator & Confusion Matrix",
            fontsize=8.4, fontweight="bold", color="#0f4c81")
    ax.text(0.35, 4.55, "Chronological Test Evaluation (N = 8,785 Cart Sessions · Strict 80:20 Time Split)",
            fontsize=6.6, color="#64748b")

    # 4 Confusion Matrix Cells
    cm_items = [
        (0.35, 3.82, "True Positive (TP · Caught)", "4,560", "70.95% of 6,427 abandoned", "#047857"),
        (2.85, 3.82, "False Positive (FP · False Alarm)", "1,018", "Completed flagged as risk", "#b45309"),
        (0.35, 3.12, "False Negative (FN · Missed)", "1,867", "29.05% abandoned missed", "#b91c1c"),
        (2.85, 3.12, "True Negative (TN · Organic)", "1,340", "56.83% specificity", "#0f4c81"),
    ]
    for cx, cy, lbl, val, sub, col in cm_items:
        ax.add_patch(mpatches.FancyBboxPatch((cx, cy), 2.40, 0.62, boxstyle="round,pad=0.02,rounding_size=0.04",
                                             fc="#f8fafc", ec="#e2e8f0", lw=0.8))
        ax.text(cx + 0.08, cy + 0.46, lbl, fontsize=6.0, fontweight="bold", color="#64748b")
        ax.text(cx + 0.08, cy + 0.22, val, fontsize=9.8, fontweight="bold", color=col, family="monospace")
        ax.text(cx + 0.95, cy + 0.22, sub, fontsize=5.8, color="#475569")

    # Threshold trade-off table
    ax.text(0.35, 2.85, "Decision Probability Threshold (τ) vs. CRM Intervention Strategy",
            fontsize=7.2, fontweight="bold", color="#0f172a")
    th_headers = ["τ", "RF Prec", "RF Rec", "RF F1", "Bal Acc", "Recommended CRM Use Case"]
    th_rows = [
        ["0.30", "0.7551", "0.9818", "0.8536", "0.5568", "Zero-cost UI badge / shipping reminder"],
        ["0.40", "0.7751", "0.9136", "0.8387", "0.5955", "Push notification / automated chat"],
        ["0.50", "0.8175", "0.7095", "0.7597", "0.6389", "Balanced retention trigger (Default)"],
        ["0.60", "0.8771", "0.4176", "0.5658", "0.6291", "Targeted 5%–10% discount voucher"],
        ["0.70", "0.9055", "0.2533", "0.3959", "0.5906", "High-value margin subsidy / VIP call"],
    ]
    col_x_th = [0.38, 0.80, 1.38, 1.95, 2.50, 3.12]
    ax.add_patch(mpatches.Rectangle((0.35, 2.50), 4.95, 0.25, fc="#f1f5f9", ec="#cbd5e1", lw=0.6))
    for cx, h_txt in zip(col_x_th, th_headers):
        ax.text(cx, 2.59, h_txt, fontsize=6.0, fontweight="bold", color="#334155")
    for r_idx, r_vals in enumerate(th_rows):
        ry = 2.20 - r_idx * 0.36
        bg = "#e0f2fe" if r_idx == 2 else "#ffffff"
        ax.add_patch(mpatches.Rectangle((0.35, ry), 4.95, 0.36, fc=bg, ec="#e2e8f0", lw=0.5))
        for c_idx, (cx, val) in enumerate(zip(col_x_th, r_vals)):
            fw = "bold" if (c_idx == 0 or r_idx == 2) else "normal"
            ax.text(cx, ry + 0.13, val, fontsize=5.9, fontweight=fw, color="#0f172a")

    # Right Card: Tab 3 Feature Drivers & Temporal Behavior
    ax.add_patch(mpatches.FancyBboxPatch((5.60, 0.20), 5.20, 4.80, boxstyle="round,pad=0.02,rounding_size=0.06",
                                         fc="#ffffff", ec="#cbd5e1", lw=1.0))
    ax.text(5.75, 4.74, "Tab 3: Feature Drivers & Empirical Temporal Risk Distribution",
            fontsize=8.4, fontweight="bold", color="#0f4c81")
    ax.text(5.75, 4.55, "Top Anti-Leakage Features at First Add-to-Cart & Day/Hour Abandonment Peaks",
            fontsize=6.6, color="#64748b")

    feats = [
        ("1. prev_sessions", 0.1995, 1.00, "Mean: 2.20 (Aband) vs 9.44 (Comp)"),
        ("2. elapsed_min", 0.1600, 0.80, "Mean: 4.26m (Aband) vs 8.89m (Comp)"),
        ("3. price_log", 0.1515, 0.76, "Mean: 11.09 (Aband) vs 11.04 (Comp)"),
        ("4. cat_freq", 0.1277, 0.64, "Mean: 260.1 (Aband) vs 221.3 (Comp)"),
        ("5. hour (UTC)", 0.1016, 0.51, "Peak risk: 09:00 UTC (85.84%)"),
        ("6. n_views_same_item", 0.0811, 0.41, "Mean: 0.91 (Aband) vs 1.18 (Comp)"),
    ]
    ax.text(5.75, 4.28, "Gini Feature Importance & Class Behavioral Comparison:", fontsize=7.0, fontweight="bold", color="#0f172a")
    for idx, (fname, gval, ratio, desc) in enumerate(feats):
        fy = 3.98 - idx * 0.28
        ax.text(5.75, fy, fname, fontsize=6.1, fontweight="bold", color="#334155")
        ax.add_patch(mpatches.Rectangle((7.20, fy - 0.03), 1.35, 0.13, fc="#e2e8f0", ec="none"))
        ax.add_patch(mpatches.Rectangle((7.20, fy - 0.03), 1.35 * ratio, 0.13, fc="#0f4c81", ec="none"))
        ax.text(8.62, fy, f"{gval:.4f}", fontsize=6.0, fontweight="bold", color="#0f4c81", family="monospace")
        ax.text(9.10, fy, desc, fontsize=5.6, color="#475569")

    # Temporal summary table in Right Card
    ax.text(5.75, 2.15, "Empirical Temporal Abandonment Extremes (Hour & Day of Week):",
            fontsize=7.0, fontweight="bold", color="#0f172a")
    t_headers = ["Temporal Window", "Abandonment Rate", "Operational Pattern"]
    t_rows = [
        ["09:00 UTC (Morning Peak)", "85.84% (Highest)", "Morning browsing & cart bookmarking surge"],
        ["12:00 UTC (Midday Peak)", "85.09% (High)", "Lunch-hour window shopping spike"],
        ["15:00 UTC (Afternoon Low)", "64.73% (Lowest)", "Highest transaction completion window (35.27%)"],
        ["Saturday & Sunday (Weekend)", "77.39% & 76.55%", "Weekend casual browsing without checkout"],
        ["Wednesday (Mid-Week Low)", "69.88% (Lowest Day)", "Strongest weekday checkout conversion"],
    ]
    col_x_t = [5.78, 7.42, 8.55]
    ax.add_patch(mpatches.Rectangle((5.75, 1.82), 4.88, 0.24, fc="#f1f5f9", ec="#cbd5e1", lw=0.6))
    for cx, h_txt in zip(col_x_t, t_headers):
        ax.text(cx, 1.90, h_txt, fontsize=6.0, fontweight="bold", color="#334155")
    for r_idx, r_vals in enumerate(t_rows):
        ry = 1.52 - r_idx * 0.28
        ax.add_patch(mpatches.Rectangle((5.75, ry), 4.88, 0.28, fc="#ffffff", ec="#e2e8f0", lw=0.5))
        for c_idx, (cx, val) in enumerate(zip(col_x_t, r_vals)):
            col_txt = "#b91c1c" if (c_idx == 1 and r_idx in (0, 1, 3)) else ("#047857" if (c_idx == 1 and r_idx in (2, 4)) else "#0f172a")
            fw = "bold" if c_idx in (0, 1) else "normal"
            ax.text(cx, ry + 0.09, val, fontsize=5.8, fontweight=fw, color=col_txt)

    plt.tight_layout(pad=0.1)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def set_run_font(run, size_pt=12, bold=False, italic=False, font_name="Times New Roman"):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"), font_name)


def format_paragraph(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, first_indent_cm=0.0, line_spacing=1.15):
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line_spacing
    pf.first_line_indent = Cm(first_indent_cm)


def add_rich_paragraph(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, first_indent_cm=1.0, size_pt=12):
    """Supports **bold** and *italic* inline markers."""
    p = doc.add_paragraph()
    format_paragraph(p, align=align, space_before=space_before, space_after=space_after, first_indent_cm=first_indent_cm)
    # Parse **bold** and *italic*
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("**", i):
            end = text.find("**", i + 2)
            if end != -1:
                tokens.append((text[i + 2:end], True, False))
                i = end + 2
                continue
        if text.startswith("*", i):
            end = text.find("*", i + 1)
            if end != -1:
                tokens.append((text[i + 1:end], False, True))
                i = end + 1
                continue
        next_star = text.find("*", i)
        if next_star == -1:
            tokens.append((text[i:], False, False))
            break
        else:
            if next_star > i:
                tokens.append((text[i:next_star], False, False))
                i = next_star
            else:
                tokens.append(("*", False, False))
                i += 1
    for txt, is_b, is_i in tokens:
        r = p.add_run(txt)
        set_run_font(r, size_pt=size_pt, bold=is_b, italic=is_i)
    return p


def add_bab_heading(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=4, first_indent_cm=0.0)
    r = p.add_run(text)
    set_run_font(r, size_pt=12, bold=True)
    return p


def add_subbab_heading(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=3, first_indent_cm=0.0)
    r = p.add_run(text)
    set_run_font(r, size_pt=12, bold=True)
    return p


def add_bullet_item(doc, text, prefix="• "):
    p = doc.add_paragraph()
    format_paragraph(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=2, first_indent_cm=0.0)
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.first_line_indent = Cm(-0.4)
    # Reuse rich parser
    full_text = prefix + text
    tokens = []
    i = 0
    n = len(full_text)
    while i < n:
        if full_text.startswith("**", i):
            end = full_text.find("**", i + 2)
            if end != -1:
                tokens.append((full_text[i + 2:end], True, False))
                i = end + 2
                continue
        if full_text.startswith("*", i):
            end = full_text.find("*", i + 1)
            if end != -1:
                tokens.append((full_text[i + 1:end], False, True))
                i = end + 1
                continue
        next_star = full_text.find("*", i)
        if next_star == -1:
            tokens.append((full_text[i:], False, False))
            break
        else:
            if next_star > i:
                tokens.append((full_text[i:next_star], False, False))
                i = next_star
            else:
                tokens.append(("*", False, False))
                i += 1
    for txt, is_b, is_i in tokens:
        r = p.add_run(txt)
        set_run_font(r, size_pt=12, bold=is_b, italic=is_i)
    return p


def set_cell_shading(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    tcPr.append(shd)


def set_cell_margins(cell, top=50, bottom=50, left=90, right=90):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def add_styled_table(doc, headers, rows, col_widths_cm=None, font_size_pt=10.5, center_cols=None):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    if center_cols is None:
        center_cols = set(range(1, len(headers)))

    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        if col_widths_cm and j < len(col_widths_cm):
            cell.width = Cm(col_widths_cm[j])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, "E2E8F0")
        set_cell_margins(cell, top=55, bottom=55, left=80, right=80)
        p = cell.paragraphs[0]
        format_paragraph(
            p,
            align=WD_ALIGN_PARAGRAPH.CENTER if j in center_cols else WD_ALIGN_PARAGRAPH.LEFT,
            space_before=1,
            space_after=1,
            first_indent_cm=0.0,
            line_spacing=1.05,
        )
        r = p.add_run(h)
        set_run_font(r, size_pt=font_size_pt, bold=True)

    for i, row_data in enumerate(rows):
        for j, val in enumerate(row_data):
            cell = tbl.cell(i + 1, j)
            if col_widths_cm and j < len(col_widths_cm):
                cell.width = Cm(col_widths_cm[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=45, bottom=45, left=80, right=80)
            p = cell.paragraphs[0]
            format_paragraph(
                p,
                align=WD_ALIGN_PARAGRAPH.CENTER if j in center_cols else WD_ALIGN_PARAGRAPH.LEFT,
                space_before=1,
                space_after=1,
                first_indent_cm=0.0,
                line_spacing=1.05,
            )
            txt = str(val)
            is_b = txt.startswith("**") and txt.endswith("**")
            if is_b:
                txt = txt[2:-2]
            r = p.add_run(txt)
            set_run_font(r, size_pt=font_size_pt, bold=is_b)

    return tbl


def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_shading(cell, "F8FAFC")
    set_cell_margins(cell, top=70, bottom=70, left=110, right=110)
    p = cell.paragraphs[0]
    format_paragraph(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=0, first_indent_cm=0.0, line_spacing=1.05)
    r = p.add_run(code_text.strip())
    set_run_font(r, size_pt=9.5, font_name="Consolas")
    return tbl


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    diag_path = os.path.join(FIG_DIR, "fig0_pipeline_architecture.png")
    dash_tab1_path = os.path.join(FIG_DIR, "fig4_dashboard_overview.png")
    dash_tab23_path = os.path.join(FIG_DIR, "fig5_dashboard_simulator.png")
    create_pipeline_diagram(diag_path)
    create_dashboard_tab1_figure(dash_tab1_path)
    create_dashboard_tab23_figure(dash_tab23_path)

    doc = docx.Document()

    # Set A4 page size & margins matching template
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.5)

    # Set default Normal style
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(12)

    # =========================================================================
    # HALAMAN JUDUL (COVER)
    # =========================================================================
    p_top = doc.add_paragraph()
    format_paragraph(p_top, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=2)
    r = p_top.add_run("LAPORAN AKHIR PROYEK")
    set_run_font(r, size_pt=16, bold=True)

    p_mk = doc.add_paragraph()
    format_paragraph(p_mk, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=18)
    r = p_mk.add_run("MATA KULIAH TEKNOLOGI BIG DATA")
    set_run_font(r, size_pt=14, bold=True)

    p_title = doc.add_paragraph()
    format_paragraph(p_title, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=24)
    r = p_title.add_run(
        "ANALISIS PERBANDINGAN PEMROSESAN BATCH DAN NEAR REAL-TIME DALAM DETEKSI DINI CART ABANDONMENT PADA PLATFORM E-COMMERCE"
    )
    set_run_font(r, size_pt=14, bold=True)

    p_disusun = doc.add_paragraph()
    format_paragraph(p_disusun, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    r = p_disusun.add_run("Disusun oleh:")
    set_run_font(r, size_pt=12, bold=True)

    p_kls = doc.add_paragraph()
    format_paragraph(p_kls, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)
    r = p_kls.add_run("Kelompok 15 — Kelas : B2")
    set_run_font(r, size_pt=12, bold=True)

    # Tabel Anggota (mengikuti format template)
    tbl_anggota = doc.add_table(rows=3, cols=2)
    tbl_anggota.style = "Table Grid"
    tbl_anggota.alignment = WD_TABLE_ALIGNMENT.CENTER
    anggota_data = [
        ("1.", "Arief Adhitya Ramadhan – J0403241055"),
        ("2.", "Muhammad Bafqi – J0403241018"),
        ("3.", "Zidan Dzulqarnain – J0403241032"),
    ]
    for idx, (no_str, nama_nim) in enumerate(anggota_data):
        c0 = tbl_anggota.cell(idx, 0)
        c1 = tbl_anggota.cell(idx, 1)
        c0.width = Cm(1.2)
        c1.width = Cm(9.5)
        set_cell_margins(c0, top=55, bottom=55, left=80, right=80)
        set_cell_margins(c1, top=55, bottom=55, left=100, right=100)
        p0 = c0.paragraphs[0]
        format_paragraph(p0, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=1, space_after=1)
        r0 = p0.add_run(no_str)
        set_run_font(r0, size_pt=12, bold=False)

        p1 = c1.paragraphs[0]
        format_paragraph(p1, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=1, space_after=1)
        r1 = p1.add_run(nama_nim)
        set_run_font(r1, size_pt=12, bold=False)

    # Logo IPB
    logo_path = os.path.join(FIG_DIR, "logo_ipb.png")
    p_logo = doc.add_paragraph()
    format_paragraph(p_logo, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=28, space_after=28)
    if os.path.exists(logo_path):
        r_logo = p_logo.add_run()
        r_logo.add_picture(logo_path, width=Cm(4.2))
    else:
        r_logo = p_logo.add_run("[LOGO IPB]")
        set_run_font(r_logo, size_pt=12, bold=True)

    p_prodi = doc.add_paragraph()
    format_paragraph(p_prodi, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=2)
    r = p_prodi.add_run("PROGRAM STUDI TEKNOLOGI REKAYASA PERANGKAT LUNAK")
    set_run_font(r, size_pt=12, bold=True)

    p_sv = doc.add_paragraph()
    format_paragraph(p_sv, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    r = p_sv.add_run("SEKOLAH VOKASI INSTITUT PERTANIAN BOGOR")
    set_run_font(r, size_pt=12, bold=True)

    p_yr = doc.add_paragraph()
    format_paragraph(p_yr, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=0)
    r = p_yr.add_run("2026")
    set_run_font(r, size_pt=12, bold=True)

    doc.add_page_break()

    # =========================================================================
    # BAB I. PENDAHULUAN
    # =========================================================================
    add_bab_heading(doc, "BAB I. PENDAHULUAN")

    add_subbab_heading(doc, "1.1 Latar Belakang")
    add_rich_paragraph(
        doc,
        "Pertumbuhan transaksi perdagangan elektronik (*e-commerce*) menghasilkan aliran data interaksi pengguna (*clickstream*) berkecepatan dan bervolume tinggi setiap detiknya, mulai dari penelusuran halaman produk (*view*), penambahan produk ke keranjang belanja (*add-to-cart*), hingga penyelesaian pembayaran (*transaction*) (Moe, 2003; Montgomery et al., 2004). Meskipun trafik kunjungan meningkat tajam terutama pada periode kampanye belanja nasional dan *flash sale*, sebagian besar sesi belanja justru berakhir tanpa pembayaran atau dikenal sebagai *shopping cart abandonment*. Literatur dan studi industri mencatat bahwa rasio *cart abandonment* pada ritel daring secara konsisten berada pada kisaran 65% hingga lebih dari 80% karena pengguna sering memanfaatkan keranjang sebagai alat pembanding harga atau ruang simpan sementara (Kukar-Kinney & Close, 2010; Rubin et al., 2020).",
    )
    add_rich_paragraph(
        doc,
        "Bagi tim pemasaran dan *Customer Relationship Management* (CRM), deteksi dini terhadap sesi yang berpotensi mengalami *cart abandonment* sangat penting untuk meluncurkan intervensi tepat waktu seperti pengingat instan (*push notification*) atau voucer terbatas. Namun, sistem analitik konvensional yang mengandalkan pemrosesan berkala (*batch processing* per jam atau harian) sering kali menghasilkan prediksi ketika sesi pengguna telah berakhir (*expired*), sehingga peluang konversi hilang (Marz & Warren, 2015; Armbrust et al., 2018). Selain itu, banyak kajian terdahulu masih mengevaluasi model menggunakan fitur akhir sesi yang rentan terhadap kebocoran informasi masa depan (*data leakage*). Oleh karena itu, proyek ini memilih topik deteksi dini *cart abandonment* pada titik *add-to-cart* pertama sekaligus membandingkan efektivitas pemrosesan *batch* dan *near real-time* (*streaming*) menggunakan teknologi *Big Data*.",
    )

    add_subbab_heading(doc, "1.2 Rumusan Masalah")
    add_rich_paragraph(
        doc,
        "Berdasarkan latar belakang tersebut, rumusan masalah utama yang diselesaikan dalam proyek ini adalah:",
        first_indent_cm=0.0,
        space_after=2,
    )
    add_bullet_item(doc, "Faktor perilaku, atribut produk (harga dan kategori), serta pola waktu apa yang paling berkaitan dengan terjadinya *cart abandonment* pada sesi belanja pengguna?", prefix="1. ")
    add_bullet_item(doc, "Bagaimana kinerja model klasifikasi *Random Forest* dibandingkan *Logistic Regression* dalam mendeteksi dini sesi berisiko *cart abandonment* pada titik observasi *add-to-cart* pertama tanpa kebocoran data (*anti-leakage*)?", prefix="2. ")
    add_bullet_item(doc, "Seberapa besar perbedaan kecepatan deteksi (latensi) dan proporsi sesi *abandonment* yang berhasil diintervensi tepat waktu (*Effective Recall*) antara arsitektur pemrosesan *batch* dan *near real-time* (*micro-batch streaming*)?", prefix="3. ")

    add_subbab_heading(doc, "1.3 Tujuan Proyek")
    add_rich_paragraph(
        doc,
        "Tujuan yang ingin dicapai melalui pengolahan dan analisis dataset dalam proyek ini meliputi:",
        first_indent_cm=0.0,
        space_after=2,
    )
    add_bullet_item(doc, "Mengidentifikasi karakteristik perilaku sesi pengguna, pola waktu (jam dan hari), serta faktor penyebab utama yang membedakan sesi transaksi selesai (*completed*) dari sesi *cart abandonment*.", prefix="1. ")
    add_bullet_item(doc, "Membangun dan mengevaluasi model klasifikasi *Random Forest* dan *Logistic Regression* berbasis 10 fitur *anti-leakage* pada titik *add-to-cart* pertama untuk memprediksi risiko *cart abandonment*.", prefix="2. ")
    add_bullet_item(doc, "Menganalisis perbandingan latensi pemrosesan dan *Effective Recall* antara pendekatan *batch* (harian dan per jam) dengan pendekatan *near real-time* (*micro-batch* dan *PySpark Structured Streaming*), serta menyajikannya ke dalam *dashboard* telemetri operasional interaktif (*Serving Layer*) untuk simulasi intervensi CRM.", prefix="3. ")

    # =========================================================================
    # BAB II. DATASET DAN METODE
    # =========================================================================
    add_bab_heading(doc, "BAB II. DATASET DAN METODE")

    add_subbab_heading(doc, "2.1 Deskripsi Dataset")
    add_rich_paragraph(
        doc,
        "Proyek ini menggunakan **Retailrocket Recommender System Dataset**, yaitu kumpulan data *clickstream* dan katalog produk dunia nyata yang dikumpulkan dari platform *e-commerce* selama 4,5 bulan (3 Mei 2015 hingga 18 September 2015 UTC). Dataset terdiri atas tiga tabel terpisah yang mencakup log aktivitas pengguna (`events.csv`), perubahan atribut produk lintas waktu (`item_properties_part1.csv` dan `item_properties_part2.csv`), serta hierarki kategori (`category_tree.csv`). Ringkasan spesifikasi dataset disajikan pada Tabel 2.1.",
    )

    p_cap1 = doc.add_paragraph()
    format_paragraph(p_cap1, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    r = p_cap1.add_run("Tabel 2.1 Deskripsi dan Spesifikasi Dataset Retailrocket")
    set_run_font(r, size_pt=11, bold=True)

    add_styled_table(
        doc,
        headers=["Informasi", "Keterangan"],
        rows=[
            ["**Nama dataset**", "Retailrocket Recommender System (E-Commerce Clickstream) Dataset"],
            ["**Sumber dataset**", "Kaggle (https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset)"],
            [
                "**Jumlah record**",
                "Total 23.033.672 baris: (1) events.csv = 2.756.101 baris (2.664.312 view, 69.332 addtocart, 22.457 transaction dari 1.407.580 visitor unik); (2) item_properties_part1 & part2.csv = 20.275.902 baris (417.053 item unik); (3) category_tree.csv = 1.669 baris.",
            ],
            [
                "**Jumlah atribut**",
                "11 atribut mentah lintas 3 tabel (5 atribut pada events.csv, 4 atribut pada item_properties, 2 atribut pada category_tree) yang ditransformasikan menjadi 10 fitur prediktif dan 1 label target per sesi.",
            ],
            [
                "**Atribut penting**",
                "Atribut Mentah: timestamp, visitorid, event, itemid, transactionid, property ('790' = harga, 'categoryid' = kategori), value.\nFitur Turunan Sesi: prev_sessions, elapsed_min, price_log, cat_freq, hour, n_views_same_item, dow, n_events_before, n_unique_items, n_views_before, dan label target abandoned (1/0).",
            ],
        ],
        col_widths_cm=[4.2, 11.3],
        font_size_pt=10.5,
        center_cols=set(),
    )

    add_subbab_heading(doc, "2.2 Tahapan Pengolahan Data")
    add_rich_paragraph(
        doc,
        "Tahapan pengolahan data dirancang mengikuti prinsip *Lambda Architecture* dan aturan pencegahan kebocoran data (*strict anti-leakage*) sebagai berikut:",
        first_indent_cm=0.0,
        space_before=4,
        space_after=2,
    )
    add_bullet_item(doc, "**Pemuatan dan Pemeriksaan Kualitas Data:** Memuat 2,75 juta rekaman `events.csv` dan mengekstraksi atribut harga (`property = '790'`) serta kategori (`property = 'categoryid'`) dari 20,27 juta baris `item_properties` secara *chunking*.", prefix="1. ")
    add_bullet_item(doc, "**Konstruksi Sesi (*Session-ization*) dan Pelabelan:** Mengonversi `timestamp` milidetik ke detik (`ts`), mengurutkan berdasarkan `visitorid` dan `ts`, serta membentuk sesi baru apabila `visitorid` berganti atau terdapat jeda inaktivitas > 30 menit (`1.800` detik). Dari 1.761.660 total sesi, disaring 43.924 sesi yang memiliki aktivitas `addtocart`. Sesi diberi label `abandoned = 1` jika tanpa `transaction` (31.992 sesi; 72,83%) dan `abandoned = 0` jika terdapat `transaction` (11.932 sesi; 27,17%).", prefix="2. ")
    add_bullet_item(doc, "**Rekayasa 10 Fitur *Anti-Leakage* pada Titik Observasi Dini:** Titik observasi ditetapkan pada kejadian `addtocart` pertama (`cart_ts`). Seluruh aktivitas setelah `cart_ts` dipangkas agar tidak terjadi *intra-session leakage*. Riwayat sesi sebelumnya (`prev_sessions`) dihitung dengan *strict expanding window* (hanya sesi masa lalu yang telah berakhir sebelum `cart_ts` saat ini, yaitu `end_ts_prev < cart_ts`).", prefix="3. ")
    add_bullet_item(doc, "**Pembagian Data Kronologis dan Imputasi:** Dataset diurutkan berdasarkan `cart_ts` dan dibagi secara kronologis menjadi 80% *Training* (35.139 sesi) dan 20% *Testing* (8.785 sesi). Nilai hilang pada harga dan kategori (1,18%) diimputasi menggunakan median harga data *Training* (`59.268,0`) serta *frequency encoding* kategori (`cat_freq`) yang dihitung murni dari data *Training*.", prefix="4. ")
    add_bullet_item(doc, "**Pemodelan, Simulasi Arsitektur Streaming, dan Penyajian Dashboard (*Serving Layer*):** Melatih model klasifikasi pada *batch layer*, menyimulasikan 5 skenario jendela waktu pemrosesan terhadap batas waktu intervensi (`deadline = end_ts + 30 menit`), menguji inferensi *near real-time* menggunakan *PySpark Structured Streaming*, serta menyajikan telemetri hasil eksperimen pada *dashboard* interaktif (`dashboard.py` berbasis *Streamlit* dan `dashboard.html` berbasis Web UI).", prefix="5. ")

    p_fig0 = doc.add_paragraph()
    format_paragraph(p_fig0, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    r_fig0 = p_fig0.add_run()
    r_fig0.add_picture(diag_path, width=Cm(15.2))

    p_cap_fig0 = doc.add_paragraph()
    format_paragraph(p_cap_fig0, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=6)
    r = p_cap_fig0.add_run("Gambar 2.1 Diagram Alur Pengolahan Data dan Arsitektur Deteksi Dini Cart Abandonment")
    set_run_font(r, size_pt=10.5, italic=True)

    add_subbab_heading(doc, "2.3 Teknologi dan Metode Analisis")
    add_rich_paragraph(
        doc,
        "Pengolahan dan eksperimen dijalankan pada lingkungan komputasi terukur dengan prosesor **12th Gen Intel(R) Core(TM) i5-12450HX** (8 *cores*, 12 *threads*), memori **11,78 GB RAM**, sistem operasi Windows 10, serta ekosistem **Python 3.11**, **Apache Spark (PySpark / Spark Structured Streaming)**, **Pandas**, **NumPy**, **Scikit-Learn**, **Matplotlib**, serta **Streamlit** dan **HTML5/JavaScript** untuk visualisasi *dashboard* telemetri interaktif. **PySpark** dipilih karena menyediakan mesin eksekusi terdistribusi *in-memory* serta API *Structured Streaming* (`readStream` dan `writeStream.foreachBatch`) yang mampu memproses aliran data *clickstream* secara *micro-batch* dengan penjaminan konsistensi *end-to-end* (Armbrust et al., 2018), sedangkan **Streamlit** dipilih pada *Serving Layer* karena mampu mengintegrasikan artefak metrik JSON/CSV dan simulasi inferensi *micro-batch* ke dalam antarmuka operasional secara langsung.",
    )
    add_rich_paragraph(
        doc,
        "Pada tahap pemodelan analitik, diterapkan metode **Classification** (didukung *Descriptive Analytics*) dengan membandingkan dua algoritma:",
        first_indent_cm=1.0,
        space_after=2,
    )
    add_bullet_item(doc, "**Random Forest Classifier (Metode Utama):** Konfigurasi `n_estimators = 200`, `max_depth = 12`, dan `class_weight = 'balanced'`. Metode ansambel pohon keputusan ini dipilih karena tangguh terhadap *noise* data *clickstream*, mampu menangkap interaksi non-linear antarfitur perilaku dan harga, tahan terhadap *overfitting*, serta menyediakan *Gini feature importance* untuk mengidentifikasi faktor pemicu *abandonment* (Baumann et al., 2018).", prefix="1. ")
    add_bullet_item(doc, "**Logistic Regression (Metode Pembanding / Baseline):** Dikonfigurasi dalam *pipeline* `StandardScaler` dengan `max_iter = 1000` dan `class_weight = 'balanced'`. Dipilih sebagai *baseline* linear berlatensi sangat rendah untuk menguji apakah peningkatan kompleksitas pada *Random Forest* tetap layak digunakan pada skenario *near real-time*.", prefix="2. ")

    # =========================================================================
    # BAB III. HASIL DAN PEMBAHASAN
    # =========================================================================
    add_bab_heading(doc, "BAB III. HASIL DAN PEMBAHASAN")

    add_subbab_heading(doc, "3.1 Hasil Pengolahan Data dengan PySpark")
    add_rich_paragraph(
        doc,
        "Proses pengolahan data berhasil mengintegrasikan 2.756.101 baris *event clickstream* dan 20.275.902 baris properti produk dalam total waktu eksekusi *end-to-end* 53,0 detik. Tahap *session-ization* menghasilkan **1.761.660 sesi keseluruhan**, di mana **43.924 sesi (2,49%)** memiliki aktivitas penambahan produk ke keranjang (`addtocart`). Dari 43.924 sesi keranjang tersebut, tercatat **31.992 sesi (72,83%) berakhir sebagai *cart abandonment*** dan hanya **11.932 sesi (27,17%) yang menyelesaikan transaksi**. Selain itu, pada data uji (8.785 sesi), median sisa durasi sesi setelah `addtocart` pertama hingga aktivitas terakhir pengguna (`end_ts - cart_ts`) sangat singkat, yaitu hanya **85,0 detik** (rata-rata 551,72 detik). Statistik deskriptif dan perbandingan rata-rata ke-10 fitur pada titik observasi dini disajikan pada Tabel 3.1.",
    )

    p_cap_t31 = doc.add_paragraph()
    format_paragraph(p_cap_t31, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    r = p_cap_t31.add_run("Tabel 3.1 Statistik fitur hasil ekstraksi pada titik add-to-cart pertama (43.924 sesi)")
    set_run_font(r, size_pt=11, bold=True)

    add_styled_table(
        doc,
        headers=["Nama Fitur", "Deskripsi Teknis", "Mean (Completed)", "Mean (Abandoned)", "Gini Importance (RF)"],
        rows=[
            ["**prev_sessions**", "Jumlah sesi masa lalu pengunjung (end_ts < cart_ts)", "9,4421", "2,1968", "**0,1995**"],
            ["**elapsed_min**", "Durasi (menit) dari awal sesi ke addtocart pertama", "8,8926", "4,2550", "**0,1600**"],
            ["**price_log**", "Transformasi ln(1 + price) dari properti 790", "11,0364", "11,0910", "**0,1515**"],
            ["**cat_freq**", "Frekuensi kategori produk pada data Training", "221,2675", "260,0601", "**0,1277**"],
            ["hour", "Jam terjadinya addtocart pertama (0–23 UTC)", "13,7849", "12,8142", "0,1016"],
            ["n_views_same_item", "Jumlah view pada item yang sama sebelum masuk keranjang", "1,1796", "0,9140", "0,0811"],
            ["dow", "Hari dalam minggu (0 = Senin s.d. 6 = Minggu)", "2,5246", "2,7416", "0,0593"],
            ["n_events_before", "Total aktivitas dalam sesi hingga addtocart pertama", "3,7596", "2,7215", "0,0435"],
            ["n_unique_items", "Jumlah produk unik dilihat sebelum addtocart pertama", "2,2710", "1,6686", "0,0397"],
            ["n_views_before", "Total aktivitas view sebelum addtocart pertama", "2,7386", "1,7215", "0,0360"],
        ],
        col_widths_cm=[3.2, 5.7, 2.2, 2.2, 2.2],
        font_size_pt=9.5,
        center_cols={2, 3, 4},
    )

    add_rich_paragraph(
        doc,
        "Selanjutnya, pada pengujian *speed layer*, diimplementasikan pemrosesan aliran data menggunakan **PySpark Structured Streaming** dengan mekanisme *atomic file rename* (1.000 sesi uji dikirim bertahap dalam 10 *chunk* CSV masing-masing 100 baris) dan interval pemicu (*trigger*) 2 detik. Potongan kode utama dan hasil *output* distribusi latensi *streaming* ditunjukkan di bawah ini:",
        space_before=4,
        space_after=3,
    )

    add_code_block(
        doc,
        """# 1. PySpark DataFrame API: Load Clickstream Events & Session-ization (Window Function)
sdf_events = spark.read.csv(f"{DATA_DIR}/events.csv", header=True, inferSchema=True)
sdf_events = sdf_events.withColumn("ts", F.floor(F.col("timestamp") / 1000))
w_visitor  = Window.partitionBy("visitorid").orderBy("ts", "timestamp")
sdf_events = sdf_events.withColumn("prev_ts", F.lag("ts").over(w_visitor))
sdf_events = sdf_events.withColumn(
    "is_new_sess", F.when(F.col("prev_ts").isNull() | ((F.col("ts") - F.col("prev_ts")) > 1800), 1).otherwise(0)
)
# Output Distribusi Event: view = 2.664.312 | addtocart = 69.332 | transaction = 22.457

# 2. PySpark Structured Streaming: Speed Layer Micro-Batch (Trigger 2 Detik, Atomic Rename)
schema = StructType([StructField(c, DoubleType()) for c in FEATURES + ["write_ts"]])
def process_batch(df, batch_id):
    if df.rdd.isEmpty(): return
    pdf = df.toPandas()
    proba = rf.predict_proba(pdf[FEATURES])[:, 1]
    lat_log.append(pd.DataFrame({"batch_id": batch_id, "latency_s": time.time() - pdf["write_ts"],
                                 "pred": (proba >= 0.5).astype(int)}))

query = (spark.readStream.schema(schema).option("header", "true").csv(STREAM_DIR)
         .writeStream.foreachBatch(process_batch).trigger(processingTime="2 seconds").start())
# Output Benchmark Streaming (1.000 baris): Mean = 1,2735 s | Median = 1,2596 s | Max = 2,0766 s""",
    )

    add_subbab_heading(doc, "3.2 Hasil Analisis atau Pemodelan")
    add_rich_paragraph(
        doc,
        "Evaluasi model klasifikasi dilakukan pada 8.785 sesi data uji kronologis (proporsi kelas positif *abandoned* 73,16%). Mengingat ketimpangan kelas (*class imbalance*), performa diukur menggunakan *Precision, Recall, F1-Score, ROC-AUC, Precision-Recall AUC (PR-AUC)*, dan *Balanced Accuracy* sebagaimana dirangkum pada Tabel 3.2.",
    )

    p_cap_t32 = doc.add_paragraph()
    format_paragraph(p_cap_t32, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    r = p_cap_t32.add_run("Tabel 3.2 Perbandingan kinerja model klasifikasi pada data uji kronologis (8.785 sesi)")
    set_run_font(r, size_pt=11, bold=True)

    add_styled_table(
        doc,
        headers=["Model", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC", "Balanced Acc", "Train (s)", "Infer (ms/baris)"],
        rows=[
            ["**Random Forest**", "**0,8175**", "0,7095", "0,7597", "**0,7030**", "**0,8574**", "**0,6389**", "1,0011", "0,006635"],
            ["Logistic Regression", "0,8036", "**0,7487**", "**0,7752**", "0,6829", "0,8420", "0,6250", "**0,0479**", "**0,000228**"],
        ],
        col_widths_cm=[3.1, 1.5, 1.4, 1.5, 1.6, 1.5, 1.8, 1.4, 1.7],
        font_size_pt=9.5,
    )

    add_rich_paragraph(
        doc,
        "Tabel 3.2 menunjukkan bahwa **Random Forest** mengungguli *Logistic Regression* pada seluruh metrik daya pisah utama, yakni **Precision (0,8175)**, **ROC-AUC (0,7030)**, **PR-AUC (0,8574)**, dan **Balanced Accuracy (0,6389)**, dengan menghasilkan 4.560 *True Positive*, 1.340 *True Negative*, 1.018 *False Positive*, dan 1.867 *False Negative* pada ambang probabilitas $\\tau = 0,50$. Selain itu, analisis sensitivitas ambang keputusan membuktikan bahwa penurunan ambang Random Forest ke $\\tau = 0,40$ mampu meningkatkan *Recall* menjadi **91,36%** dan *F1-Score* menjadi **0,8387** (dengan *Precision* 77,51%), sedangkan penaikan ambang ke $\\tau = 0,60$ meningkatkan *Precision* hingga **87,71%**. Kecepatan inferensi Random Forest sebesar **0,006635 ms/baris** (±150.000 prediksi/detik) membuktikan bahwa model ansambel ini sangat ringan untuk dieksekusi secara *real-time*.",
        space_before=4,
    )

    # Gambar Feature Importance & Pola Waktu
    fig1_path = os.path.join(FIG_DIR, "fig1_feature_importance.png")
    fig2_path = os.path.join(FIG_DIR, "fig2_temporal_patterns.png")
    fig3_path = os.path.join(FIG_DIR, "fig3_latency_effective_recall.png")

    if os.path.exists(fig1_path):
        p_f1 = doc.add_paragraph()
        format_paragraph(p_f1, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=1)
        p_f1.add_run().add_picture(fig1_path, width=Cm(12.8))
        p_cf1 = doc.add_paragraph()
        format_paragraph(p_cf1, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)
        r = p_cf1.add_run("Gambar 3.1 Urutan tingkat kepentingan fitur (Gini Importance) pada model Random Forest")
        set_run_font(r, size_pt=10.5, italic=True)

    if os.path.exists(fig2_path):
        p_f2 = doc.add_paragraph()
        format_paragraph(p_f2, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=1)
        p_f2.add_run().add_picture(fig2_path, width=Cm(14.5))
        p_cf2 = doc.add_paragraph()
        format_paragraph(p_cf2, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)
        r = p_cf2.add_run("Gambar 3.2 Pola tingkat cart abandonment berdasarkan (a) jam (UTC) dan (b) hari dalam minggu")
        set_run_font(r, size_pt=10.5, italic=True)

    add_rich_paragraph(
        doc,
        "Selanjutnya, hasil simulasi perbandingan arsitektur pemrosesan *Batch* dan *Near Real-Time* menggunakan model Random Forest yang sama terhadap batas waktu intervensi (`deadline = end_ts + 1.800 detik`) disajikan pada Tabel 3.3 dan Gambar 3.3.",
    )

    p_cap_t33 = doc.add_paragraph()
    format_paragraph(p_cap_t33, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    r = p_cap_t33.add_run("Tabel 3.3 Perbandingan latensi pemrosesan dan Effective Recall lintas skenario arsitektur")
    set_run_font(r, size_pt=11, bold=True)

    add_styled_table(
        doc,
        headers=["Mode Pemrosesan", "Jendela W (s)", "Mean Latency (s)", "Median Latency (s)", "Keputusan < Deadline", "TP Tepat Waktu", "Effective Recall"],
        rows=[
            ["Batch Harian (24 Jam)", "86.400", "37.343,62", "26.765,00", "3,60%", "113 / 6.427", "0,0176"],
            ["Batch Per Jam (1 Jam)", "3.600", "1.792,34", "1.788,00", "60,47%", "2.512 / 6.427", "0,3909"],
            ["**Micro-Batch (5 Menit)**", "**300**", "**150,21**", "**149,00**", "**100,00%**", "**4.560 / 6.427**", "**0,7095**"],
            ["**Near Real-Time (1 Menit)**", "**60**", "**30,51**", "**30,00**", "**100,00%**", "**4.560 / 6.427**", "**0,7095**"],
            ["**Near Real-Time (10 Detik)**", "**10**", "**5,52**", "**5,00**", "**100,00%**", "**4.560 / 6.427**", "**0,7095**"],
        ],
        col_widths_cm=[3.6, 1.8, 2.2, 2.2, 2.0, 2.0, 1.7],
        font_size_pt=9.5,
    )

    if os.path.exists(fig3_path):
        p_f3 = doc.add_paragraph()
        format_paragraph(p_f3, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=1)
        p_f3.add_run().add_picture(fig3_path, width=Cm(13.2))
        p_cf3 = doc.add_paragraph()
        format_paragraph(p_cf3, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)
        r = p_cf3.add_run("Gambar 3.3 Perbandingan Effective Recall (%) dan persentase keputusan tepat waktu lintas jendela arsitektur")
        set_run_font(r, size_pt=10.5, italic=True)

    add_rich_paragraph(
        doc,
        "Sebagai wujud implementasi *Serving Layer* pada *Lambda Architecture*, hasil pemodelan dan telemetri *streaming* diintegrasikan ke dalam **Operational Telemetry Dashboard** yang dibangun dalam dua artefak siap pakai, yakni aplikasi **Streamlit (`dashboard.py`)** serta antarmuka web mandiri **HTML5/JavaScript (`dashboard.html`)** sebagaimana ditunjukkan pada Gambar 3.4. Dashboard ini memiliki bilah telemetri global (*6-Card KPI Strip*) dan tiga panel navigasi interaktif: (1) **Tab 1 (*Batch vs. Near Real-Time & Live Stream*)** untuk menyimulasikan dampak pemilihan jendela pemrosesan terhadap *Effective Recall* sekaligus memutar ulang *scoring* aliran sesi *micro-batch* (*trigger* 2 detik) beserta rekomendasi aksi CRM otomatis; (2) **Tab 2 (*Model Performance & Threshold $\\tau$ Simulator*)** untuk meninjau *Confusion Matrix* dan menguji sensitivitas ambang probabilitas ($\\tau \\in [0,30; 0,70]$); serta (3) **Tab 3 (*Feature Drivers & Temporal Behavior*)** untuk memantau kontribusi 10 fitur *anti-leakage* dan jam/hari paling rawan *abandonment*.",
        space_before=4,
    )

    if os.path.exists(dash_tab1_path):
        p_f4 = doc.add_paragraph()
        format_paragraph(p_f4, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=1)
        p_f4.add_run().add_picture(dash_tab1_path, width=Cm(15.2))
        p_cf4 = doc.add_paragraph()
        format_paragraph(p_cf4, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)
        r = p_cf4.add_run("Gambar 3.4 Tampilan antarmuka Operational Telemetry Dashboard (Serving Layer): perbandingan jendela arsitektur dan simulasi Live Micro-Batch Streaming (2s Trigger)")
        set_run_font(r, size_pt=10.5, italic=True)

    add_subbab_heading(doc, "3.3 Interpretasi Hasil dan Rekomendasi")
    add_rich_paragraph(
        doc,
        "Berdasarkan hasil pengolahan data dan pemodelan di atas, diperoleh tiga temuan penting yang menjawab permasalahan utama proyek:",
        first_indent_cm=0.0,
        space_after=2,
    )
    add_bullet_item(doc, "**Temuan 1 — Determinan Perilaku dan Harga pada Titik Add-to-Cart Pertama:** Berdasarkan Gambar 3.1 dan Tabel 3.1, tiga fitur teratas menyumbang lebih dari 51% daya pisah model, yaitu riwayat sesi sebelumnya (`prev_sessions` = 0,1995), durasi eksplorasi menuju keranjang (`elapsed_min` = 0,1600), dan logaritma harga produk (`price_log` = 0,1515). Pengunjung yang meninggalkan keranjang memiliki rata-rata riwayat kunjungan jauh lebih sedikit (2,20 vs. 9,44 sesi) dan durasi eksplorasi separuh lebih singkat (4,26 vs. 8,89 menit) dibandingkan pengunjung yang menyelesaikan pembayaran. Hal ini membuktikan bahwa penambahan barang ke keranjang secara tergesa-gesa oleh pengunjung baru umumnya berfungsi sebagai *bookmark* atau pembanding harga sementara.", prefix="1. ")
    add_bullet_item(doc, "**Temuan 2 — Pola Kerawanan Waktu (Jam dan Akhir Pekan):** Gambar 3.2 menunjukkan bahwa tingkat *cart abandonment* memuncak pada pukul 08:00–12:00 UTC (tertinggi pukul 09:00 UTC sebesar 85,84%) serta meningkat signifikan pada akhir pekan, yakni hari Sabtu (77,39%) dan Minggu (76,55%), dibandingkan pertengahan minggu seperti Rabu (69,88%). Sebaliknya, konversi pembelian terbaik terjadi pada sore hari pukul 15:00–19:00 UTC.", prefix="2. ")
    add_bullet_item(doc, "**Temuan 3 — Degradasi Drastis Effective Recall pada Pemrosesan Batch:** Tabel 3.3 dan Gambar 3.3 membuktikan bahwa model ML yang akurat secara *offline* kehilangan nilai bisnisnya apabila dijalankan pada pemrosesan *batch*. Pada **Batch Harian (24 jam)**, rata-rata waktu tunggu keputusan mencapai 10,37 jam sehingga 96,40% sesi telah kedaluwarsa dan **Effective Recall anjlok dari 0,7095 menjadi 0,0176** (kehilangan 97,5% potensi intervensi). Pada **Batch Per Jam**, *Effective Recall* masih tergerus hampir separuhnya menjadi **0,3909**. Sebaliknya, arsitektur **Micro-Batch (≤ 5 menit)** dan **Near Real-Time Streaming (10–60 detik)** berhasil mencapai **100% keputusan tepat waktu** dengan *Effective Recall* utuh **0,7095** dan latensi *end-to-end* rata-rata **1,27 detik**.", prefix="3. ")

    add_rich_paragraph(
        doc,
        "Berdasarkan temuan tersebut, rekomendasi yang dapat diberikan bagi pengelola platform *e-commerce* adalah:",
        first_indent_cm=0.0,
        space_before=4,
        space_after=2,
    )
    add_bullet_item(doc, "**Adopsi Arsitektur Lambda dengan Speed Layer Berjendela ≤ 60 Detik:** Mengganti penjadwalan *batch* harian/jam untuk *scoring* keranjang belanja menjadi *micro-batch streaming* (menggunakan *PySpark Structured Streaming* dengan *trigger* 2–10 detik) agar intervensi terkirim saat pengguna masih berada di layar (mengingat median sisa sesi pasca-*add-to-cart* hanya 85 detik).", prefix="• ")
    add_bullet_item(doc, "**Strategi Intervensi Berjenjang Berbasis Ambang Probabilitas pada Dashboard Operasional (Threshold-Driven CRM):** Memanfaatkan fitur simulator ambang keputusan ($\\tau$) pada *dashboard* operasional untuk memicu intervensi berbiaya nol seperti *in-app pop-up reminder* pada ambang rendah ($\\tau = 0,40$, *Recall* 91,36%), serta memicu voucer diskon 5%–10% atau gratis ongkos kirim pada ambang tinggi ($\\tau = 0,60$, *Precision* 87,71%) khusus bagi pengunjung baru (`prev_sessions = 0`) agar tidak menggerus margin keuntungan.", prefix="• ")

    # =========================================================================
    # BAB IV. KESIMPULAN
    # =========================================================================
    add_bab_heading(doc, "BAB IV. KESIMPULAN")
    add_rich_paragraph(
        doc,
        "Proyek ini berhasil merancang, mengimplementasikan, dan mengevaluasi *pipeline* deteksi dini *cart abandonment* berbasis *Big Data* pada dataset *clickstream* Retailrocket (2.756.101 *event* dan 20.275.902 baris atribut produk yang membentuk 43.924 sesi keranjang belanja dengan tingkat *abandonment* 72,83%). Pertama, dari sisi faktor perilaku dan pola waktu, *cart abandonment* paling dipengaruhi oleh rendahnya riwayat sesi pengunjung (`prev_sessions`), singkatnya waktu eksplorasi sebelum barang masuk keranjang (`elapsed_min`), dan harga produk (`price_log`), dengan waktu paling rawan terjadi pada pukul 08:00–12:00 UTC serta akhir pekan (Sabtu–Minggu). Kedua, dari sisi pemodelan *anti-leakage* pada titik `addtocart` pertama, algoritma **Random Forest** terbukti unggul dengan **Precision 0,8175, ROC-AUC 0,7030, PR-AUC 0,8574, dan Balanced Accuracy 0,6389**, serta waktu inferensi sangat cepat sebesar **0,006635 ms/baris**.",
    )
    add_rich_paragraph(
        doc,
        "Ketiga, simulasi latensi arsitektur membuktikan bahwa pemrosesan **Batch Harian** dan **Batch Per Jam** menurunkan *Effective Recall* secara tajam menjadi **0,0176** dan **0,3909** akibat keputusan prediksi yang terlambat melewati batas waktu intervensi sesi. Sebaliknya, implementasi **Micro-Batch (≤ 5 menit)** dan **Near Real-Time PySpark Structured Streaming (10–60 detik)** mampu menjaga **100% keputusan sebelum batas waktu** dengan **Effective Recall penuh 0,7095** (peningkatan 40,3 kali lipat dibanding *Batch Harian*) dan rata-rata latensi *streaming end-to-end* **1,2735 detik**. Seluruh hasil pemodelan dan telemetri *streaming* tersebut juga telah berhasil diintegrasikan ke dalam *dashboard* operasional interaktif (`dashboard.py` dan `dashboard.html`) sebagai *Serving Layer* untuk mendukung simulasi ambang keputusan dan intervensi CRM secara *real-time*. Sebagai saran pengembangan ke depan, penelitian selanjutnya dapat mengintegrasikan *point-in-time join* untuk melacak perubahan harga dinamis per milidetik, menguji model sekuensial berbasis *deep learning* (seperti GRU/Transformer), serta menggelar *pipeline* pada klaster terdistribusi Apache Kafka multi-broker secara langsung.",
    )

    # =========================================================================
    # DAFTAR PUSTAKA
    # =========================================================================
    doc.add_page_break()
    add_bab_heading(doc, "DAFTAR PUSTAKA")

    refs = [
        "Armbrust, M., Das, T., Torres, J., Yavuz, B., Zhu, S., Xin, R., Ghodsi, A., Stoica, I., & Zaharia, M. (2018). Structured streaming: A declarative API for real-time applications in Apache Spark. Proceedings of the 2018 International Conference on Management of Data (SIGMOD), 601–613. https://doi.org/10.1145/3183713.3190664",
        "Baumann, A., Haupt, J., Gebert, F., & Lessmann, S. (2018). Changing perspectives: Using graph metrics to predict purchase probabilities in e-commerce. Expert Systems with Applications, 94, 137–148. https://doi.org/10.1016/j.eswa.2017.10.046",
        "Cirqueira, D., Hofer, M., Nedbal, D., Helfert, M., & Bezbradica, M. (2020). Customer purchase behavior prediction in e-commerce: A conceptual framework and research agenda. New Frontiers in Mining Complex Patterns (NFMCP 2019), Lecture Notes in Computer Science, 11985, 119–136. https://doi.org/10.1007/978-3-030-48861-1_8",
        "Kukar-Kinney, M., & Close, A. G. (2010). The determinants of consumers’ online shopping cart abandonment. Journal of the Academy of Marketing Science, 38(2), 240–250. https://doi.org/10.1007/s11747-009-0141-5",
        "Marz, N., & Warren, J. (2015). Big Data: Principles and best practices of scalable real-time data systems. Manning Publications. https://www.manning.com/books/big-data",
        "Moe, W. W. (2003). Buying, searching, or browsing: Differentiating between online shoppers using in-store navigational clickstream. Journal of Consumer Psychology, 13(1–2), 29–39. https://doi.org/10.1207/S15327663JCP13-1&2_03",
        "Montgomery, A. L., Li, S., Srinivasan, K., & Liechty, J. C. (2004). Modeling online browsing and path analysis using clickstream data. Marketing Science, 23(4), 579–595. https://doi.org/10.1287/mksc.1040.0073",
        "Retailrocket. (2017). Retailrocket recommender system dataset [Data set]. Kaggle. https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset",
        "Rubin, D., Martins, C., Ilyuk, V., & Hildebrand, L. (2020). The effects of perceived diagnosticity on online shopping cart abandonment. Journal of Retailing and Consumer Services, 52, 101911. https://doi.org/10.1016/j.jretconser.2019.101911",
        "Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLOS ONE, 10(3), e0118432. https://doi.org/10.1371/journal.pone.0118432",
        "Sakar, C. O., Polat, S. O., Katircioglu, M., & Kastro, Y. (2019). Real-time prediction of online shoppers’ purchasing intention using multilayer perceptron and LSTM recurrent neural networks. Neural Computing and Applications, 31(10), 6893–6908. https://doi.org/10.1007/s00521-018-3523-0",
        "Zhao, H., Wang, S., & Chen, Y. (2021). Understanding mobile shopping cart abandonment: An integration of behavioral and contextual factors. Electronic Commerce Research and Applications, 46, 101032. https://doi.org/10.1016/j.elerap.2021.101032",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        format_paragraph(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, first_indent_cm=0.0)
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        r = p.add_run(ref)
        set_run_font(r, size_pt=12)

    # =========================================================================
    # LAMPIRAN
    # =========================================================================
    add_bab_heading(doc, "LAMPIRAN")

    add_rich_paragraph(
        doc,
        "**1. Tautan Notebook, Kode Program, dan Artefak Dashboard:**",
        first_indent_cm=0.0,
        space_before=2,
        space_after=2,
    )
    add_bullet_item(doc, "**Google Colab Notebook (Dapat Diakses & Diperiksa):** https://colab.research.google.com/drive/1Kuy5iaNErqbCnsOe4CVORHmc4eETJy9X")
    add_bullet_item(doc, "**Sumber Dataset Kaggle Retailrocket:** https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset")
    add_bullet_item(doc, "**Artefak Kode Pipeline & Pengujian pada Workspace:** `Project_Big_Data_Kelompok_15.ipynb`, `src/pipeline_core.py`, `src/run_experiment.py`, dan `tests/test_pipeline_core.py`.")
    add_bullet_item(doc, "**Artefak Operational Telemetry Dashboard (Serving Layer):** `dashboard.py` (dijalankan melalui perintah `streamlit run dashboard.py`) dan `dashboard.html` (antarmuka web mandiri HTML5/CSS3/JS yang dapat dibuka langsung pada peramban).")

    add_rich_paragraph(
        doc,
        "**2. Dokumentasi Tabel Sensitivitas Ambang Keputusan (Threshold):**",
        first_indent_cm=0.0,
        space_before=6,
        space_after=2,
    )

    p_cap_lamp = doc.add_paragraph()
    format_paragraph(p_cap_lamp, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    r = p_cap_lamp.add_run("Tabel L.1 Analisis Sensitivitas Ambang Probabilitas (Threshold) pada Data Uji (8.785 Sesi)")
    set_run_font(r, size_pt=11, bold=True)

    add_styled_table(
        doc,
        headers=["Model", "Threshold (τ)", "Precision", "Recall", "F1-Score", "Balanced Accuracy"],
        rows=[
            ["Random Forest", "0,30", "0,7551", "**0,9818**", "**0,8536**", "0,5568"],
            ["Random Forest", "0,40", "0,7751", "0,9136", "0,8387", "0,5955"],
            ["**Random Forest**", "**0,50**", "**0,8175**", "**0,7095**", "**0,7597**", "**0,6389**"],
            ["Random Forest", "0,60", "0,8771", "0,4176", "0,5658", "0,6291"],
            ["Random Forest", "0,70", "**0,9055**", "0,2533", "0,3959", "0,5906"],
            ["Logistic Regression", "0,30", "0,7584", "0,9687", "0,8508", "0,5639"],
            ["Logistic Regression", "0,40", "0,7694", "0,9225", "0,8390", "0,5845"],
            ["Logistic Regression", "0,50", "0,8036", "0,7487", "0,7752", "0,6250"],
            ["Logistic Regression", "0,60", "0,8690", "0,2983", "0,4441", "0,5879"],
            ["Logistic Regression", "0,70", "0,9369", "0,0300", "0,0582", "0,5123"],
        ],
        col_widths_cm=[4.0, 2.3, 2.2, 2.2, 2.2, 2.6],
        font_size_pt=10.0,
    )

    add_rich_paragraph(
        doc,
        "**3. Dokumentasi Antarmuka dan Implementasi Kode Dashboard Operasional (Serving Layer):**",
        first_indent_cm=0.0,
        space_before=8,
        space_after=2,
    )
    add_rich_paragraph(
        doc,
        "Dashboard operasional dirancang untuk menjembatani metrik hasil eksperimen (`outputs/metrics_summary.json`) dan *stream scoring* ke dalam antarmuka pengambilan keputusan CRM. Spesifikasi komponen pada ketiga tab disajikan pada Tabel L.2, visualisasi antarmuka simulator Tab 2 dan Tab 3 ditunjukkan pada Gambar L.1, sedangkan potongan kode utama `dashboard.py` disajikan di bawahnya.",
        first_indent_cm=1.0,
        space_before=0,
        space_after=4,
    )

    p_cap_lamp2 = doc.add_paragraph()
    format_paragraph(p_cap_lamp2, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    r = p_cap_lamp2.add_run("Tabel L.2 Spesifikasi Modul dan Komponen Interaktif pada Dashboard Telemetri Cart Abandonment")
    set_run_font(r, size_pt=11, bold=True)

    add_styled_table(
        doc,
        headers=["Modul / Panel Dashboard", "Komponen Visual & Kontrol Interaktif", "Fungsi Operasional bagi Tim Analitik / CRM"],
        rows=[
            [
                "**Global Telemetry Strip & Sidebar**",
                "6 kartu KPI utama (Total Events, Cart Sessions, Abandonment Rate 72,83%, RF PR-AUC 0,8574, Median Remaining Time 85,0s, Effective Recall Gain 40,3×) serta kontrol pemilih jendela arsitektur & slider ambang τ.",
                "Memantau kesehatan trafik *clickstream*, sisa waktu intervensi sesi, dan spesifikasi perangkat keras dasar secara sekilas.",
            ],
            [
                "**Tab 1: Batch vs. Near Real-Time & Live Stream**",
                "Grafik dan tabel interaktif 5 mode jendela arsitektur, metrik benchmark *Speed Layer* (mean 1,2735s), serta simulator *Live Micro-Batch Stream* (pemicu 2 detik).",
                "Membandingkan penyusutan *Effective Recall* pada *batch* vs. *streaming* dan mensimulasikan rekomendasi aksi CRM per sesi secara *real-time*.",
            ],
            [
                "**Tab 2: Model Performance & Threshold (τ) Simulator**",
                "Tabel komparasi Random Forest vs. Logistic Regression, 4 kartu *Confusion Matrix* (TP=4.560, FP=1.018, FN=1.867, TN=1.340), dan simulator ambang τ (0,30 s.d. 0,70).",
                "Menyesuaikan ambang batas probabilitas *abandonment* dengan anggaran promosi (notifikasi gratis pada τ rendah vs. voucer diskon pada τ tinggi).",
            ],
            [
                "**Tab 3: Feature Drivers & Temporal Behavior**",
                "Grafik batang *Gini Importance* 10 fitur *anti-leakage*, tabel rata-rata kelas (*Completed* vs. *Abandoned*), dan distribusi *abandonment* per jam (UTC) & hari.",
                "Mengidentifikasi faktor pemicu utama (`prev_sessions`, `elapsed_min`, `price_log`) serta menjadwalkan kampanye retensi pada jam/hari paling rawan.",
            ],
        ],
        col_widths_cm=[3.8, 6.2, 5.5],
        font_size_pt=9.5,
        center_cols=set(),
    )

    if os.path.exists(dash_tab23_path):
        p_fl1 = doc.add_paragraph()
        format_paragraph(p_fl1, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=1)
        p_fl1.add_run().add_picture(dash_tab23_path, width=Cm(15.2))
        p_cfl1 = doc.add_paragraph()
        format_paragraph(p_cfl1, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)
        r = p_cfl1.add_run("Gambar L.1 Tampilan panel Tab 2 (Interactive Decision Threshold τ Simulator & Confusion Matrix) dan Tab 3 (Feature Drivers & Empirical Temporal Risk Distribution) pada Dashboard")
        set_run_font(r, size_pt=10.5, italic=True)

    add_code_block(
        doc,
        """# Potongan Kode Utama: dashboard.py (Streamlit Operational Telemetry Dashboard)
import json, time, pandas as pd, streamlit as st

st.set_page_config(page_title="Cart Abandonment Telemetry — Kelompok 15", layout="wide")
with open("outputs/metrics_summary.json", "r", encoding="utf-8") as f:
    summary = json.load(f)

ds, sim_df = summary["dataset"], pd.DataFrame(summary["latency_simulation"])
thresh_df  = pd.DataFrame(summary["threshold_sensitivity"])

# Sidebar Interactive Simulation Controls
with st.sidebar:
    selected_window = st.selectbox("Processing Window Mode", options=sim_df["mode"].tolist(), index=2)
    selected_thresh = st.select_slider("Decision Probability Threshold (τ)", options=[0.3, 0.4, 0.5, 0.6, 0.7], value=0.5)

# Top KPI Telemetry Strip (6 Operational Metrics)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Events", f"{ds['total_events']:,}", f"{ds['total_all_sessions']:,} sessions")
k2.metric("Cart Sessions", f"{ds['total_cart_sessions']:,}", f"Test: {ds['test_sessions']:,}")
k3.metric("Abandonment Rate", f"{ds['abandoned_rate_pct']}%", f"{ds['abandoned_count']:,} abandoned")
k4.metric("RF PR-AUC", "0.8574", "ROC-AUC: 0.7030")
k5.metric("Median Remaining Time", f"{ds['session_remaining_sec_median']} s", "After 1st addtocart")
win_row = sim_df[sim_df["mode"] == selected_window].iloc[0]
k6.metric("Effective Recall", f"{win_row['effective_recall']:.4f}", f"{win_row['pct_decided_before_deadline']:.1f}% < deadline")""",
    )

    doc.save(OUT_DOCX)
    print(f"Saved: {OUT_DOCX}")


if __name__ == "__main__":
    main()
