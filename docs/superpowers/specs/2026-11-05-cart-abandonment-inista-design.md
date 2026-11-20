# Desain Eksperimen & Naskah Jurnal INISTA: Deteksi Dini Cart Abandonment Berbasis Big Data

## 1. Tujuan & Konteks (Intent & Why)
Platform e-commerce menghadapi tingginya tingkat *cart abandonment* (pengguna meninggalkan keranjang belanja tanpa menyelesaikan transaksi), terutama saat lonjakan trafik seperti *flash sale*. Pemrosesan data secara *batch* berkala menyebabkan keterlambatan deteksi, sehingga intervensi marketing/CRM (seperti pengingat atau promo instan) baru terkirim setelah pengguna meninggalkan platform. Proyek ini bertujuan:
1. Membangun pipeline deteksi dini *cart abandonment* bebas kebocoran data (*anti-leakage*) pada titik observasi `addtocart` pertama menggunakan dataset clickstream nyata **Retailrocket**.
2. Membandingkan model klasifikasi **Random Forest** dan **Logistic Regression** pada kondisi ketimpangan kelas (*class imbalance*).
3. Mengevaluasi dampak latensi pemrosesan (**Batch** vs. **Near Real-Time / Streaming**) terhadap efektivitas intervensi menggunakan metrik **Effective Recall**.
4. Menyusun luaran akhir berupa **Naskah Jurnal Ilmiah sesuai format INISTA (SINTA 4)** yang sekaligus mencakup dokumentasi teknis **Worksheet 4 (WS4)**.

## 2. Goals, Non-Goals, & Anti-Goals
- **Goals:**
  - Mengeksekusi pipeline secara lokal pada dataset penuh Retailrocket (`c:\Users\muham\Downloads\archive (5)`).
  - Menerapkan aturan *anti-leakage* ketat pada ekstraksi 10 fitur (termasuk *expanding window* untuk `prev_sessions` dengan syarat `end_ts < cart_ts` dan *time-based split* 80:20 berdasarkan `cart_ts`).
  - Mengukur performa model dengan metrik **Precision, Recall, F1-Score, ROC-AUC, PR-AUC (Average Precision), Balanced Accuracy**, waktu *training* (s), dan latensi inferensi per baris (ms), termasuk analisis pergeseran *threshold*.
  - Menyimulasikan 5 skenario jendela pemrosesan (86.400s, 3.600s, 300s, 60s, 10s) dengan formulasi matematis **Effective Recall** terhadap batas waktu intervensi (`end_ts + 30 menit`), serta menguji pipeline *micro-batch streaming* dengan *atomic file rename* dan *trigger* 2 detik.
  - Menghasilkan grafik beresolusi tinggi (`dpi=300`) yang ramah cetak hitam-putih (*black-and-white hardcopy*) menggunakan kombinasi pola arsiran (`hatch`), gaya garis (`linestyle`), dan penanda titik (`marker`).
  - Menyusun draft lengkap jurnal **INISTA** dengan sitasi IEEE (`[1]`, `[2]`) dari literatur mutakhir (5–10 tahun terakhir).
- **Non-Goals:**
  - Membangun klaster produksi multi-node (Kafka/HDFS terdistribusi di cloud).
  - Menggunakan data sintetis untuk fitur di luar dataset Retailrocket.
- **Anti-Goals:**
  - *Data leakage* lintas waktu (menghitung statistik imputasi/encoding pada seluruh data sebelum *split*, atau memasukkan sesi yang belum selesai ke dalam `prev_sessions`).
  - Grafik yang hanya mengandalkan perbedaan warna tanpa pola arsiran/marker sehingga tidak terbaca saat dicetak hitam-putih.

## 3. Pendekatan yang Dipertimbangkan (Approaches)
1. **Pendekatan 1 — Eksekusi Lokal Terintegrasi di `.venv` + Penyusunan Jurnal (Dipilih):**
   Membuat *virtual environment* Python 3.11 lokal di `c:\Bafqi\Big Data`, menjalankan keseluruhan eksperimen pada file CSV asli di `c:\Users\muham\Downloads\archive (5)`, mencatat spesifikasi perangkat keras riil (CPU, RAM, OS, versi library), menyimpan metrik ke JSON/CSV dan grafik 300 DPI, lalu menyusun naskah jurnal INISTA. Dilengkapi mekanisme *fallback* streaming Python murni dengan *atomic file rename* dan *trigger* 2 detik apabila PySpark di Windows terkendala `HADOOP_HOME`/`winutils.exe`.
2. **Pendekatan 2 — Eksekusi Manual di Google Colab (Ditolak):**
   Mengunggah ±900 MB dataset ke Google Drive/Colab secara manual. Tidak efisien dan memutus otomasi verifikasi data ke dalam naskah jurnal.

## 4. Spesifikasi Teknis & Metodologis (Keputusan yang Dikunci)
1. **Session-ization & Pelabelan:**
   - Sesi baru terbentuk jika `visitorid` berganti atau selisih waktu antar-event > 1.800 detik (30 menit).
   - Populasi analisis adalah seluruh sesi yang memiliki minimal satu event `addtocart`. Label `abandoned = 1` jika sesi tidak memiliki event `transaction`, dan `0` jika memiliki minimal satu `transaction`.
2. **Anti-Leakage & Split Kronologis:**
   - Titik observasi adalah `cart_ts` (timestamp event `addtocart` pertama dalam sesi).
   - Fitur `prev_sessions` dihitung secara ketat sebagai jumlah sesi masa lalu milik `visitorid` yang sama yang telah **berakhir sebelum titik observasi sesi saat ini** ($\text{end\_ts}_{\text{prev}} < \text{cart\_ts}_{\text{current}}$).
   - Urutan dataset dan pemotongan **Training (80% awal)** vs **Testing (20% akhir)** didasarkan pada `cart_ts` agar tidak ada tumpang tindih informasi lintas waktu.
   - Median `price` dan frekuensi kategori (`cat_freq`) dihitung **hanya pada data Training** dan dipetakan ke data Testing.
3. **Evaluasi Imbalance & Model:**
   - Model: **Random Forest** (`n_estimators=200, max_depth=12, class_weight="balanced", random_state=42`) vs **Logistic Regression** (`StandardScaler + LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)`).
   - Metrik wajib: **Precision, Recall, F1-Score, ROC-AUC, PR-AUC (`average_precision_score`), Balanced Accuracy (`balanced_accuracy_score`)**, waktu *training* (detik), dan waktu inferensi (ms/baris).
   - Eksperimen sensitivitas *threshold* probabilitas (mis. 0.3, 0.4, 0.5, 0.6, 0.7) untuk melihat trade-off Precision vs Recall.
4. **Formulasi Matematis Simulasi Latensi & Effective Recall:**
   - Untuk ukuran jendela pemrosesan $W \in \{86400, 3600, 300, 60, 10\}$ detik, waktu keputusan sistem adalah:
     $$t_{\text{decision}} = \left(\lfloor t_{\text{cart}} / W \rfloor + 1\right) \times W + t_{\text{infer}}$$
   - Batas waktu intervensi efektif (*deadline*) didefinisikan sebagai berakhirnya sesi ditambah ambang inaktivitas 30 menit:
     $$t_{\text{deadline}} = t_{\text{end}} + 1800$$
   - Rumus **Effective Recall**:
     $$\text{Effective Recall} = \frac{\text{TP}_{\text{terdeteksi sebelum deadline}}}{\text{Total Aktual Abandoned (TP + FN)}}$$
     di mana $\text{TP}_{\text{terdeteksi sebelum deadline}}$ adalah sesi dengan $y = 1$, $\hat{y} = 1$, dan $t_{\text{decision}} \le t_{\text{deadline}}$.
5. **Spesifikasi Visualisasi Hitam-Putih (Standar INISTA):**
   - Semua gambar disimpan dengan `dpi=300` dalam skema warna kontras tinggi (grayscale/hitam-putih):
     - `fig1_feature_importance.png`: Horizontal bar chart dengan pola arsiran (`hatch`) dan label nilai di ujung bar.
     - `fig2_temporal_patterns.png`: Bar chart tingkat *abandonment* per jam dan per hari dengan kombinasi pola arsiran (`'//'`, `'..'`, `'xx'`).
     - `fig3_latency_effective_recall.png`: Dual-series/line plot perbandingan skenario jendela waktu menggunakan kombinasi gaya garis dan penanda titik (`'-o'`, `'--s'`, `':^'`).
6. **Lingkungan Perangkat Keras &Standar Sitasi INISTA:**
   - Mencatat spesifikasi perangkat keras pengujian secara otomatis (prosesor, kapasitas RAM, sistem operasi, versi Python dan pustaka di `.venv`) untuk dilaporkan di Bab III (*Research Method*).
   - Format penulisan mengikuti template **INISTA** (Abstract ≤ 200 kata, 4–8 kata kunci urut abjad, heading angka Romawi I–V, caption tabel angka Romawi di atas tabel, caption gambar angka Arab di bawah gambar, sitasi IEEE `[1]` dengan referensi mutakhir).
