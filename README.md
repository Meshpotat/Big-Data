# Deteksi Dini Cart Abandonment E-Commerce (Batch vs. Near Real-Time) — Kelompok 15

Proyek akhir mata kuliah **Teknologi Big Data** (Sekolah Vokasi IPB University) untuk mendeteksi potensi *cart abandonment* secara dini tepat pada kejadian `addtocart` pertama menggunakan dataset clickstream **Retailrocket**, sekaligus membandingkan efektivitas pemrosesan **Batch** vs. **Near Real-Time / Micro-Batch Streaming**.

**Anggota Kelompok 15:**
- Arief Adhitya Ramadhan (`J0403241055`)
- Muhammad Bafqi (`J0403241018`)
- Zidan Dzulqarnain (`J0403241032`)

---

## Fitur Utama Dashboard (`dashboard.py` & `dashboard.html`)

Dashboard berperan sebagai **Visualization / Serving Layer (Streamlit)** dalam rancangan *6-Layer End-to-End E-Commerce Lambda Architecture* (Worksheet 2):

1. **Speed Layer — Live Micro-Batch Stream (Random Forest vs. Logistic Regression):**
   - Menulis berkas *chunk* sesi uji nyata Retailrocket secara bertahap dengan *atomic file rename* (`os.replace`, trigger 2 detik) sebagai simulasi *streaming* Apache Kafka + Spark Structured Streaming, lalu memprediksi kedua model sekaligus secara *live* berdampingan.
   - Mengukur *Live Accuracy*, *Flagged At-Risk (%)*, *Mean End-to-End Latency (ms)*, dan *Last Batch Inference (ms)* secara nyata.
2. **Serving Layer — Real-Time Single-Session Predictor (RF vs. LR):**
   - Simulator interaktif 10 fitur perilaku pembeli (dilengkapi 3 *preset* cepat) untuk melihat probabilitas batal *checkout*, rekomendasi aksi CRM, dan waktu inferensi per baris secara berdampingan antara Random Forest dan Logistic Regression.
3. **Batch vs. Speed Layer — Model Benchmark & Effective Recall:**
   - Perbandingan lengkap metrik uji kronologis (`N = 8,785`), *Confusion Matrix*, sensitivitas *threshold* ($\tau \in [0.30, 0.70]$), dan simulasi **Effective Recall** lintas 5 jendela arsitektur (86.400s s.d. 10s).
4. **Analytics Layer — Feature Drivers & Temporal EDA:**
   - Visualisasi *Gini Feature Importance* dan pola tingkat *abandonment* berdasarkan jam (UTC) dan hari dalam minggu.
5. **End-to-End Architecture (WS2 Blueprint vs. Prototype):**
   - Diagram *6-Layer + Cross-Cutting Lambda Architecture* (`Data Sources` → `Ingestion` → `Storage` → `Processing` → `Analytics` → `Serving` + `Orchestration & Monitoring`), tabel pemetaan komponen rancangan produksi WS2 vs. prototipe implementasi, justifikasi skala *Big Data* (3V), serta posisi proyek sebagai realisasi Fokus Analitik #3 (*Cart Abandonment*). *(Tersedia juga secara native di Tab 4 `dashboard.html`.)*

---

## Ringkasan Hasil Eksperimen (Retailrocket Dataset — Google Colab Apache Spark 4.0.5)

- **Dataset & Sesi:** `2,756,101` events & `20,275,902` baris properti item $\rightarrow$ `1,761,660` sesi total (GAP 30 menit) $\rightarrow$ `43,924` sesi keranjang (`72.83%` *abandoned* vs. `27.17%` *completed*).
- **Pembagian Kronologis (80:20 berdasarkan `cart_ts`):** `35,139` sesi *Train* dan `8,785` sesi *Test*.
- **Performa Model ($\tau = 0.50$):**
  - **Random Forest:** Precision `0.8083`, Recall `0.7475`, F1 `0.7767`, ROC-AUC `0.7004`, **PR-AUC `0.8560`**, Balanced Acc `0.6322` (Peak Balanced Acc `0.6343` pada $\tau = 0.60$).
  - **Logistic Regression:** Precision `0.8036`, Recall `0.7487`, F1 `0.7752`, ROC-AUC `0.6829`, PR-AUC `0.8420`, Balanced Acc `0.6250`.
- **Simulasi Effective Recall (Batas Waktu = $t_{\text{end}} + 1800\text{ s}$):**
  - Batch Harian (86.400s): `0.0198` (`3.60%` tepat waktu, `127 / 6,427` TP)
  - Batch Per Jam (3.600s): `0.4129` (`60.47%` tepat waktu, `2,654 / 6,427` TP)
  - Micro-Batch (300s) / Near Real-Time (60s, 10s): `0.7475` (`100.00%` tepat waktu, `4,804 / 6,427` TP — **37,8×** dibanding Batch Harian)
- **PySpark Structured Streaming Benchmark (Trigger 2 Detik, 1.000 Sesi):** Mean `1.9262 s` (`1.93 s`), Median `2.0410 s`, Q1 `1.2318 s`, Q3 `2.4356 s`, Max `3.0805 s`.

---

## Cara Menjalankan Dashboard Secara Lokal

```powershell
# 1. Buat & aktifkan virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instal dependensi
pip install -r requirements.txt

# 3. Jalankan dashboard interaktif Streamlit
streamlit run dashboard.py
```

*(Cadangan statis tanpa Python dapat dibuka langsung melalui `dashboard.html` di browser.)*

---

## Menjalankan Pengujian (`pytest`)

```powershell
pip install -r requirements-dev.txt
pytest tests/test_pipeline_core.py -v
```

---

## Struktur Direktori

```text
├── dashboard.py                 # Aplikasi Streamlit live dual-model (RF vs. LR)
├── dashboard.html               # Dashboard web statis standalone (cadangan presentasi)
├── requirements.txt             # Dependensi runtime dashboard & pipeline
├── requirements-dev.txt         # Dependensi pengujian & generator dokumen
├── src/
│   ├── pipeline_core.py         # Session-ization, anti-leakage split, & Effective Recall
│   ├── serving.py               # Live single-session scoring & atomic micro-batch stream
│   ├── run_experiment.py        # Pipeline eksperimen penuh & grafik 300 DPI
│   ├── generate_ipynb.py
│   ├── generate_jict_docx.py
│   ├── generate_laporan_akhir_docx.py
│   └── generate_pptx.py
├── tests/
│   └── test_pipeline_core.py    # Unit & end-to-end tests (pytest + Streamlit AppTest)
├── outputs/
│   ├── rf_model.joblib          # Model terlatih Random Forest
│   ├── lr_model.joblib          # Model terlatih Logistic Regression
│   ├── test_stream_pool.csv     # 8.785 sesi uji kronologis Retailrocket
│   ├── serving_meta.json
│   ├── metrics_summary.json
│   └── figures/                 # Grafik publikasi 300 DPI & arsitektur
└── WS4_Rancangan_Teknis_dan_Implementasi_Kelompok_15.md
```

