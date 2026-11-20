# Cart Abandonment Early Detection & INISTA Journal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Menjalankan pipeline eksperimen deteksi dini *cart abandonment* bebas *data leakage* pada dataset Retailrocket secara lokal, menghasilkan seluruh tabel metrik (termasuk PR-AUC & Effective Recall) serta grafik standar hitam-putih 300 DPI, dan menyusun naskah lengkap jurnal INISTA (SINTA 4) beserta rangkuman teknis WS4.

**Architecture:** Pipeline modular berbasis Python 3.11 (`.venv`) yang memproses data clickstream Retailrocket (~2,75 juta event dan ~20,27 juta baris properti item) melalui tahapan *session-ization* (ambang 30 menit), ekstraksi 10 fitur *anti-leakage* pada titik `addtocart` pertama, pelatihan & evaluasi model (*Random Forest* vs *Logistic Regression*), simulasi *Effective Recall* lintas 5 jendela waktu (*batch* vs *near real-time*), dan pengujian *micro-batch streaming* dengan *atomic file rename* (PySpark Structured Streaming dengan *fallback* Python native di Windows). Seluruh metrik diekspor ke JSON/CSV dan divisualisasikan ke PNG 300 DPI ramah cetak hitam-putih untuk diintegrasikan langsung ke naskah jurnal INISTA.

**Tech Stack:** Python 3.11, `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `psutil`, `pyspark` (opsional dengan fallback micro-batch streaming native).

**Spec:** `c:\Bafqi\Big Data\docs\superpowers\specs\2026-11-05-cart-abandonment-inista-design.md`

## Global Constraints

- Dataset dibaca langsung dari `c:\Users\muham\Downloads\archive (5)` (`events.csv`, `item_properties_part1.csv`, `item_properties_part2.csv`, `category_tree.csv`) tanpa mengubah atau menghapus file asli.
- Seluruh dependensi Python wajib diinstal di dalam virtual environment `c:\Bafqi\Big Data\.venv` (bukan global).
- Aturan *anti-leakage* wajib dipatuhi: (1) fitur dihitung hanya dari event hingga `addtocart` pertama (`row <= cart_row`), (2) `prev_sessions` hanya menghitung sesi milik `visitorid` yang sama yang telah selesai sebelum titik observasi sesi saat ini (`end_ts < cart_ts`), (3) pembagian data Train (80%) dan Test (20%) diurutkan berdasarkan `cart_ts`, dan (4) nilai median `price` serta `cat_freq` dihitung hanya pada data Train lalu dipetakan ke Test.
- Grafik wajib disimpan dengan `dpi=300` di `c:\Bafqi\Big Data\outputs\figures\` menggunakan pola arsiran (`hatch` seperti `'//'`, `'..'`, `'xx'`) pada bar chart dan kombinasi gaya garis/penanda (`'-o'`, `'--s'`, `':^'`) pada line plot agar terbaca jelas saat dicetak hitam-putih sesuai pedoman INISTA.
- Naskah jurnal INISTA wajib mematuhi struktur template: Abstract ≤ 200 kata, 4–8 kata kunci urut abjad, bagian I. Introduction s.d. V. Conclusion, penomoran Tabel dengan angka Romawi (`TABLE I`) di atas tabel, penomoran Gambar dengan angka Arab (`Fig. 1.`) di bawah gambar, persamaan matematika bernomor `(1)` rata kanan, dan sitasi IEEE (`[1]`, `[2]`) dari literatur mutakhir.

## Review Focus

- **Kebocoran fitur `prev_sessions` pada sesi paralel/bertumpuk:** Jika seorang pengunjung memiliki sesi sebelumnya atau perhitungan hanya memakai `cumcount()` berdasarkan `start_ts`, sesi yang belum berakhir saat `cart_ts` dapat ikut terhitung. Test harus memastikan hanya sesi dengan `end_ts < cart_ts` yang dihitung.
- **Kategori atau harga tidak dikenal (*unseen category / missing price*) di data Test:** Saat `cat_freq` dan median `price` dihitung hanya di data Train, item di data Test yang memiliki `categoryid` baru harus memetakan `cat_freq = 0` (bukan `NaN`), dan `price` kosong harus terisi median Train.
- **Perhitungan `Effective Recall` saat prediksi tepat tetapi terlambat:** Sesi *abandoned* (`y = 1`) yang diprediksi positif (`pred = 1`) tetapi memiliki `decision_ts > end_ts + 1800` tidak boleh dihitung sebagai *effective hit* di pembilang `Effective Recall`.
- **Kegagalan PySpark di Windows karena `HADOOP_HOME` / `winutils.exe` belum terkonfigurasi:** Step 8 (streaming) harus menangkap exception inisialisasi/eksekusi PySpark di Windows secara bersih dan menjalankan *micro-batch file streaming runner* berbasis thread + *atomic file rename* (`os.replace`) dengan trigger 2 detik yang identik tanpa menghentikan pipeline.
- **Batas jumlah kata Abstract INISTA:** Abstract jurnal tidak boleh melebihi 200 kata dan kata kunci harus terdiri atas 4–8 istilah yang diurutkan secara alfabetis.

---

### Task 1: Persiapan Virtual Environment, Deteksi Spesifikasi Perangkat Keras, dan Modul Anti-Leakage Core

**Files:**
- Create: `c:\Bafqi\Big Data\src\pipeline_core.py`
- Create: `c:\Bafqi\Big Data\tests\test_pipeline_core.py`

**Interfaces:**
- Consumes: Raw DataFrames atau file CSV Retailrocket (`events.csv`, `item_properties_part*.csv`).
- Produces:
  - `get_hardware_specs() -> dict`
  - `build_sessions_and_labels(events_df: pd.DataFrame, gap_s: int = 1800) -> tuple[pd.DataFrame, pd.DataFrame]`
  - `compute_strict_prev_sessions(all_sessions_df: pd.DataFrame, cart_sessions_df: pd.DataFrame) -> pd.Series`
  - `split_and_encode_features(df: pd.DataFrame, train_ratio: float = 0.8) -> tuple[pd.DataFrame, pd.DataFrame, dict]`
  - `compute_latency_simulation(test_df: pd.DataFrame, pred_te: np.ndarray, infer_s: float, window_s: int, label: str, gap_s: int = 1800) -> dict`

- [ ] **Step 1: Buat virtual environment `.venv` dan instal paket yang dibutuhkan**

Run:
```powershell
python -m venv "c:\Bafqi\Big Data\.venv"
& "c:\Bafqi\Big Data\.venv\Scripts\pip.exe" install --upgrade pip
& "c:\Bafqi\Big Data\.venv\Scripts\pip.exe" install numpy pandas scikit-learn matplotlib psutil pytest pyspark
```
Expected: Instalasi sukses tanpa error.

- [ ] **Step 2: Tulis unit test di `c:\Bafqi\Big Data\tests\test_pipeline_core.py` untuk menguji aturan anti-leakage (`prev_sessions`, `cat_freq`/median `price` split, dan rumus `Effective Recall`)**

```python
import numpy as np
import pandas as pd
from src.pipeline_core import (
    compute_strict_prev_sessions,
    split_and_encode_features,
    compute_latency_simulation,
)

def test_strict_prev_sessions_excludes_overlapping_or_future_sessions():
    all_sess = pd.DataFrame({
        "session_id": [1, 2, 3],
        "visitorid": [10, 10, 10],
        "start_ts": [100, 500, 1000],
        "end_ts": [300, 900, 1200],
    })
    cart_sess = pd.DataFrame({
        "session_id": [1, 2, 3],
        "visitorid": [10, 10, 10],
        "cart_ts": [150, 600, 850],  # sess 3 cart_ts=850 terjadi sebelum sess 2 end_ts=900
    })
    prev = compute_strict_prev_sessions(all_sess, cart_sess)
    assert list(prev) == [0, 1, 1]

def test_split_and_encode_features_prevents_test_leakage():
    df = pd.DataFrame({
        "session_id": [1, 2, 3, 4, 5],
        "cart_ts": [10, 20, 30, 40, 50],
        "price": [100.0, 200.0, 300.0, np.nan, np.nan],
        "categoryid": [10, 10, 20, 20, 999],  # 999 hanya ada di test
        "n_events_before": [1, 2, 1, 3, 2],
        "n_views_before": [0, 1, 0, 2, 1],
        "n_unique_items": [1, 1, 1, 2, 1],
        "n_views_same_item": [0, 1, 0, 1, 1],
        "elapsed_min": [0.0, 1.0, 0.5, 2.0, 1.5],
        "hour": [10, 11, 12, 13, 14],
        "dow": [0, 1, 2, 3, 4],
        "prev_sessions": [0, 0, 1, 0, 2],
        "abandoned": [1, 0, 1, 1, 1],
    })
    train_df, test_df, meta = split_and_encode_features(df, train_ratio=0.8)
    assert len(train_df) == 4
    assert len(test_df) == 1
    assert meta["train_price_median"] == 200.0
    assert test_df["price"].iloc[0] == 200.0
    assert test_df["cat_freq"].iloc[0] == 0

def test_compute_latency_simulation_effective_recall():
    test_df = pd.DataFrame({
        "cart_ts": [100, 100, 100],
        "end_ts": [200, 200, 200],
        "abandoned": [1, 1, 0],
    })
    pred_te = np.array([1, 1, 0])
    # Untuk window 3600s, decision_ts = 3600, sedangkan deadline = 200 + 1800 = 2000 (terlambat)
    res_late = compute_latency_simulation(test_df, pred_te, infer_s=0.01, window_s=3600, label="Batch 1h", gap_s=1800)
    assert res_late["effective_recall"] == 0.0
    # Untuk window 60s, decision_ts = 120 <= 2000 (tepat waktu)
    res_fast = compute_latency_simulation(test_df, pred_te, infer_s=0.01, window_s=60, label="NRT 1m", gap_s=1800)
    assert res_fast["effective_recall"] == 1.0
```

- [ ] **Step 3: Jalankan pytest untuk memastikan test gagal sebelum implementasi**

Run: `& "c:\Bafqi\Big Data\.venv\Scripts\pytest.exe" "c:\Bafqi\Big Data\tests\test_pipeline_core.py" -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'src.pipeline_core'`).

- [ ] **Step 4: Implementasikan `c:\Bafqi\Big Data\src\pipeline_core.py`**

Implementasikan fungsi-fungsi di `src/pipeline_core.py`:
- `get_hardware_specs() -> dict`: mengambil nama prosesor, jumlah core/thread, total RAM (GB) via `psutil`, versi OS Windows, versi Python, serta versi `pandas`, `numpy`, `scikit-learn`, dan `pyspark`.
- `compute_strict_prev_sessions(all_sessions_df, cart_sessions_df) -> pd.Series`: untuk setiap baris di `cart_sessions_df`, hitung jumlah sesi milik `visitorid` yang sama pada `all_sessions_df` yang memenuhi `end_ts < cart_ts` menggunakan `np.searchsorted` per grup `visitorid` agar sangat cepat pada ratusan ribu sesi.
- `split_and_encode_features(df, train_ratio=0.8)`: urutkan `df` berdasarkan `cart_ts` secara menaik, potong 80% awal sebagai `train_df` dan 20% akhir sebagai `test_df`. Hitung `train_price_median = train_df["price"].median()` dan `cat_counts = train_df["categoryid"].value_counts()`, lalu terapkan ke `train_df` dan `test_df` untuk membentuk `price_log` dan `cat_freq` (kategori baru di test diisi `0`).
- `compute_latency_simulation(test_df, pred_te, infer_s, window_s, label, gap_s=1800)`: mengimplementasikan rumus `decision_ts = (np.floor(test_df["cart_ts"] / window_s) + 1) * window_s`, `latency = decision_ts - test_df["cart_ts"] + infer_s`, `deadline = test_df["end_ts"] + gap_s`, `reachable = (decision_ts + infer_s) <= deadline`, dan `effective_recall = ((pred_te == 1) & (test_df["abandoned"] == 1) & reachable).sum() / (test_df["abandoned"] == 1).sum()`.

- [ ] **Step 5: Jalankan kembali pytest untuk memverifikasi seluruh test lulus**

Run: `& "c:\Bafqi\Big Data\.venv\Scripts\pytest.exe" "c:\Bafqi\Big Data\tests\test_pipeline_core.py" -v`
Expected: PASS (3 passed).

---

### Task 2: Eksekusi Pipeline Eksperimen Lengkap & Pembuatan Grafik Hitam-Putih 300 DPI Standar INISTA

**Files:**
- Create: `c:\Bafqi\Big Data\src\run_experiment.py`
- Create: `c:\Bafqi\Big Data\outputs\metrics_summary.json` (generated)
- Create: `c:\Bafqi\Big Data\outputs\figures\fig1_feature_importance.png` (generated)
- Create: `c:\Bafqi\Big Data\outputs\figures\fig2_temporal_patterns.png` (generated)
- Create: `c:\Bafqi\Big Data\outputs\figures\fig3_latency_effective_recall.png` (generated)

**Interfaces:**
- Consumes: `src.pipeline_core`, dataset CSV di `c:\Users\muham\Downloads\archive (5)`.
- Produces: File ringkasan JSON `outputs/metrics_summary.json`, tabel CSV di `outputs/`, dan 3 grafik PNG 300 DPI di `outputs/figures/`.

- [ ] **Step 1: Buat script `c:\Bafqi\Big Data\src\run_experiment.py` yang menjalankan Step 1–8 dan menghasilkan metrik serta visualisasi standar INISTA**

Script harus mencakup:
1. Membaca `events.csv` dari `c:\Users\muham\Downloads\archive (5)`, mencatat jumlah baris total, distribusi `view`/`addtocart`/`transaction`, jumlah `visitorid` unik, dan rentang tanggal dataset.
2. Melakukan *session-ization* (`GAP = 1800` detik), memfilter sesi dengan `addtocart`, memberi label `abandoned`, menghitung `prev_sessions` secara ketat (`end_ts < cart_ts`), mengekstraksi fitur pra-`addtocart` pertama, dan menggabungkan properti `790` (harga) serta `categoryid` dari `item_properties_part1.csv` dan `item_properties_part2.csv`.
3. Melakukan *time-based split* 80:20 berdasarkan `cart_ts` dan encoding bebas *data leakage*.
4. Melatih **Random Forest** (`n_estimators=200, max_depth=12, class_weight="balanced", n_jobs=-1, random_state=42`) dan **Logistic Regression** (`StandardScaler + LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)`), lalu menghitung **Precision, Recall, F1-Score, ROC-AUC, PR-AUC (`average_precision_score`), Balanced Accuracy (`balanced_accuracy_score`)**, waktu *training* (s), dan waktu inferensi (ms/baris).
5. Mengevaluasi sensitivitas *threshold* (0.30, 0.40, 0.50, 0.60, 0.70) pada Random Forest dan Logistic Regression.
6. Menjalankan simulasi latensi pada 5 skenario jendela waktu (`86400`, `3600`, `300`, `60`, `10` detik) untuk membandingkan *Mean Latency*, *Median Latency*, *% Decided Before Deadline*, dan *Effective Recall*.
7. Menjalankan pengujian *micro-batch streaming* (10 file chunk @ 100 baris, jeda 3 detik, *atomic file rename*, trigger 2 detik) menggunakan PySpark Structured Streaming jika Java/Hadoop tersedia, atau otomatis beralih ke *Python Micro-Batch File Streaming Runner* yang identik jika PySpark di Windows mengalami kendala environment, serta mencatat distribusi latensi *end-to-end* (`count`, `mean`, `std`, `min`, `25%`, `50%`, `75%`, `max`).
8. Menyimpan 3 grafik `dpi=300` ramah cetak hitam-putih (*grayscale + hatching + distinct markers/linestyles*):
   - `fig1_feature_importance.png`: Horizontal bar chart `feature_importances_` Random Forest dengan pola arsiran `'//'` dan angka nilai di ujung batang.
   - `fig2_temporal_patterns.png`: Subplot 2 panel (a) Abandonment Rate per Jam (`hatch='//'`) dan (b) Abandonment Rate per Hari (`hatch='..'`).
   - `fig3_latency_effective_recall.png`: Plot komparasi 5 jendela pemrosesan yang menampilkan *Effective Recall (%)* (`'-o'`) dan *% Decided Before Deadline* (`'--s'`) terhadap skala jendela waktu.

- [ ] **Step 2: Jalankan `run_experiment.py` dan verifikasi kelengkapan output**

Run: `& "c:\Bafqi\Big Data\.venv\Scripts\python.exe" "c:\Bafqi\Big Data\src\run_experiment.py"`
Expected: Script berjalan hingga selesai, mencetak seluruh tabel hasil ke terminal, menghasilkan `c:\Bafqi\Big Data\outputs\metrics_summary.json` dan ketiga file PNG di `c:\Bafqi\Big Data\outputs\figures\`.

- [ ] **Step 3: Periksa secara visual ketiga gambar grafik dan file `metrics_summary.json`**

Gunakan `read_file` pada `c:\Bafqi\Big Data\outputs\metrics_summary.json` serta ketiga gambar di `c:\Bafqi\Big Data\outputs\figures\` untuk memastikan teks jelas, kontras hitam-putih tajam, arsiran terlihat, dan tidak ada label yang terpotong.

---

### Task 3: Penyusunan Draft Jurnal Ilmiah INISTA (SINTA 4) & Dokumen Teknis WS4

**Files:**
- Create: `c:\Bafqi\Big Data\Draft_Jurnal_INISTA_Kelompok_15.md`
- Create: `c:\Bafqi\Big Data\WS4_Rancangan_Teknis_dan_Implementasi_Kelompok_15.md`

**Interfaces:**
- Consumes: `c:\Bafqi\Big Data\outputs\metrics_summary.json`, gambar di `c:\Bafqi\Big Data\outputs\figures\`, dan spesifikasi template INISTA.
- Produces: Naskah lengkap jurnal INISTA siap pakai dan dokumen teknis WS4.

- [ ] **Step 1: Susun naskah lengkap `c:\Bafqi\Big Data\Draft_Jurnal_INISTA_Kelompok_15.md` sesuai pedoman INISTA**

Pastikan seluruh elemen berikut terpenuhi secara presisi:
- **Judul & Penulis:** Judul dikapitalisasi sesuai aturan INISTA; penulis: Arief Adhitya Ramadhan, Muhammad Bafqi, Zidan Dzulqarnain beserta afiliasi dan email.
- **Abstract & Keywords:** Abstract ≤ 200 kata (memuat tujuan, prosedur, temuan kuantitatif utama dari `metrics_summary.json`, dan kesimpulan); diikuti 4–8 kata kunci yang diurutkan secara alfabetis.
- **I. Introduction:** Latar belakang pertumbuhan transaksi e-commerce dan fenomena *cart abandonment* saat kampanye belanja/*flash sale*, permasalahan keterlambatan deteksi pada pemrosesan *batch* tradisional, serta solusi deteksi dini berbasis arsitektur Lambda (*batch* vs *near real-time*) yang diusulkan.
- **II. Literature Review:** Sintesis kritis minimal 12 referensi ilmiah mutakhir (5–10 tahun terakhir, sitasi IEEE `[1]`–`[12]`) yang membahas perilaku *cart abandonment*, prediksi berbasis *clickstream machine learning*, dan perbandingan arsitektur pemrosesan *batch* vs *streaming*, diakhiri dengan pemetaan *research gap* (studi terdahulu fokus pada akurasi *offline* statis tanpa mengevaluasi penyusutan *Effective Recall* akibat latensi jendela pemrosesan).
- **III. Research Method:** Spesifikasi perangkat keras pengujian lokal (CPU Intel Core i5-12450HX, RAM, OS, versi pustaka), deskripsi dataset Retailrocket, prosedur *session-ization* (ambang 30 menit), aturan *anti-leakage* ketat pada titik observasi `addtocart` pertama (termasuk formulasi *expanding window* `prev_sessions` dan *time-based split* 80:20), konfigurasi model *Random Forest* vs *Logistic Regression*, serta definisi matematis bernomor `(1)`, `(2)`, `(3)` untuk waktu keputusan jendela pemrosesan, batas intervensi (*deadline*), dan **Effective Recall**.
- **IV. Results and Discussion:**
  - Statistik deskriptif sesi & rasio ketimpangan kelas (*abandoned* vs *completed*).
  - `TABLE I` (komparasi Precision, Recall, F1, ROC-AUC, PR-AUC, Balanced Accuracy, waktu *training*, dan waktu inferensi ms/baris antara Random Forest dan Logistic Regression) serta `TABLE II` (analisis sensitivitas *threshold*).
  - Analisis faktor penyebab melalui `Fig. 1.` (*Feature Importance*) dan pola temporal melalui `Fig. 2.` (jam dan hari).
  - `TABLE III` dan `Fig. 3.` (komparasi 5 skenario jendela waktu dari Batch Harian 86.400s hingga Near Real-Time 10s terhadap *Effective Recall*), ditambah `TABLE IV` hasil pengujian latensi *end-to-end* pada *micro-batch streaming* (trigger 2 detik).
  - Diskusi implikasi praktis bagi sistem CRM e-commerce serta bagian eksplisit mengenai keterbatasan penelitian (asumsi batas waktu intervensi 30 menit, penggunaan nilai terakhir atribut produk `item_properties`, cakupan satu periode dataset, dan simulasi streaming berbasis file).
- **V. Conclusion, Acknowledgment, & References:** Kesimpulan kuantitatif yang menjawab seluruh pertanyaan penelitian serta daftar pustaka bergaya IEEE/INISTA yang lengkap dan konsisten dengan sitasi di dalam teks.

- [ ] **Step 2: Susun dokumen `c:\Bafqi\Big Data\WS4_Rancangan_Teknis_dan_Implementasi_Kelompok_15.md`**

Rangkum tahapan teknis implementasi pipeline, arsitektur eksekusi, potongan kode inti yang sudah bebas *data leakage*, tabel hasil eksperimen, dan interpretasi singkat agar kelompok memiliki dokumen khusus yang siap dikumpulkan jika dosen menagih lembar kerja WS4 secara terpisah dari draft jurnal.

- [ ] **Step 3: Verifikasi kepatuhan format INISTA pada draft jurnal**

Periksa bahwa:
1. Jumlah kata pada *Abstract* ≤ 200 kata.
2. Kata kunci berjumlah 4–8 dan berurutan secara alfabetis.
3. Seluruh angka di dalam teks dan tabel sama persis dengan output `metrics_summary.json`.
4. Tabel menggunakan angka Romawi (`TABLE I`, `TABLE II`, dst.) dengan *caption* di atas tabel, dan Gambar menggunakan angka Arab (`Fig. 1.`, `Fig. 2.`, `Fig. 3.`) dengan *caption* di bawah gambar.
