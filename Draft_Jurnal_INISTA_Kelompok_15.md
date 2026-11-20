# Comparative Analysis of Batch and Near Real-Time Processing for Early Cart Abandonment Detection in E-Commerce Platforms Using Big Data

**Arief Adhitya Ramadhan #1, Muhammad Bafqi #2, Zidan Dzulqarnain #3**

# School of Vocational Studies, IPB University  
Bogor, Indonesia  
1 ariefadhitya@apps.ipb.ac.id  
2 muhammadbafqi@apps.ipb.ac.id  
3 zidandzulqarnain@apps.ipb.ac.id  

*Received on dd-mm-yyyy, revised on dd-mm-yyyy, accepted on dd-mm-yyyy*

---

## ***Abstract***
**Cart abandonment represents a critical revenue leakage in e-commerce platforms, particularly during high-traffic promotional campaigns. Traditional batch processing pipelines often fail to detect at-risk sessions before users leave the platform. This study investigates early cart abandonment detection at the first add-to-cart event and evaluates the operational trade-off between batch and near real-time processing architectures. Using the Retailrocket clickstream dataset comprising 2,756,101 events and 20,275,902 item property records, we constructed 43,924 cart sessions with a 30-minute inactivity threshold (72.83% abandoned). Ten strictly anti-leakage behavioral, product, and temporal features were extracted and evaluated using chronological 80:20 splitting across Random Forest and Logistic Regression classifiers. Experimental results show that Random Forest achieves the highest discriminative performance with a Precision of 0.8175, ROC-AUC of 0.7030, PR-AUC of 0.8574, and Balanced Accuracy of 0.6389, while prior session history (`prev_sessions`), elapsed time to cart (`elapsed_min`), and log item price (`price_log`) emerge as the primary predictors. Latency simulations demonstrate that daily batch (86,400 s) and hourly batch (3,600 s) reduce Effective Recall to 0.0176 and 0.3909, whereas micro-batch (300 s) and near real-time streaming preserve the full 0.7095 Effective Recall with a 1.2735 s mean end-to-end streaming latency.**

**Keywords:** *batch processing, big data analytics, cart abandonment, clickstream classification, e-commerce, near real-time streaming, random forest*

---

## I. INTRODUCTION

### *A. Background*
Perdagangan elektronik (*e-commerce*) modern menghasilkan aliran data interaksi pengguna (*clickstream*) berkecepatan dan bervolume tinggi setiap detiknya, mulai dari penelusuran halaman produk (*view*), penambahan produk ke keranjang belanja (*add-to-cart*), hingga penyelesaian pembayaran (*transaction*) [1], [2]. Meskipun trafik kunjungan dan aktivitas keranjang belanja terus meningkat—terutama pada periode kampanye belanja nasional dan *flash sale*—mayoritas sesi keranjang belanja justru berakhir tanpa transaksi, sebuah fenomena yang dikenal sebagai *shopping cart abandonment* [3], [4]. Studi industri maupun literatur akademik secara konsisten melaporkan bahwa tingkat *cart abandonment* pada platform ritel daring berkisar antara 65% hingga lebih dari 80% [4], [5]. Pengguna sering kali menggunakan keranjang belanja sebagai alat pembanding harga, ruang simpan sementara (*wish list*), atau meninggalkan sesi akibat hambatan harga dan waktu tunggu keputusan [6].

Bagi tim pemasaran dan *Customer Relationship Management* (CRM), kemampuan untuk mendeteksi secara dini sesi pengguna yang berpotensi meninggalkan keranjang merupakan kunci untuk meluncurkan intervensi tepat waktu, seperti pengingat instan (*push notification*), penawaran kupon terbatas, atau bantuan layanan pelanggan otomatis [7]. Namun, nilai bisnis dari prediksi *machine learning* pada kasus ini sangat bergantung pada dua dimensi yang saling mengikat: akurasi klasifikasi pada titik observasi awal dan kecepatan sistem pemrosesan data (*pipeline latency*) dalam menghasilkan keputusan sebelum pengguna benar-benar meninggalkan sesi [8], [9].

### *B. Problem Formulation*
Sebagian besar infrastruktur analitik e-commerce konvensional masih mengandalkan pemrosesan berkala (*batch processing*), di mana log interaksi dikumpulkan dan dieksekusi setiap satu jam atau satu hari sekali menggunakan penjadwalan *batch* [8]. Pendekatan ini menimbulkan masalah struktural: ketika model analitik baru menyelesaikan inferensi pada akhir jendela *batch*, sesi pengguna yang bersangkutan telah lama berakhir (*expired*), sehingga intervensi pemasaran kehilangan relevansi operasionalnya [9], [10]. Di sisi lain, penelitian terdahulu di bidang prediksi *cart abandonment* dan konversi pembelian umumnya hanya mengevaluasi performa model secara statis (*offline accuracy/AUC*) atau menggunakan fitur dari keseluruhan sesi yang baru diketahui setelah sesi berakhir (*post-session features*), yang secara metodologis menimbulkan kebocoran informasi masa depan (*data leakage*) [5], [11]. Oleh karena itu, diperlukan evaluasi komprehensif yang memadukan ekstraksi fitur bebas kebocoran (*anti-leakage*) pada titik *add-to-cart* pertama dengan kuantifikasi penyusutan efektivitas deteksi (*Effective Recall*) lintas jendela pemrosesan *batch* hingga *near real-time*.

### *C. Proposed Solution and Objectives*
Penelitian ini mengusulkan rancangan dan evaluasi pipeline deteksi dini *cart abandonment* berbasis *Lambda Architecture* yang membandingkan pemrosesan *batch* dan *near real-time* (*micro-batch streaming*) pada dataset clickstream nyata **Retailrocket**. Kontribusi utama dari penelitian ini meliputi:
1. Merancang skema ekstraksi 10 fitur perilaku, produk, dan temporal yang sepenuhnya bebas *data leakage* pada titik observasi `addtocart` pertama, termasuk perhitungan riwayat sesi kumulatif yang ketat ($\text{end\_ts}_{\text{prev}} < \text{cart\_ts}_{\text{current}}$) dan pembagian data kronologis (*time-based split* 80:20).
2. Mengevaluasi dan membandingkan performa klasifikasi **Random Forest** dan **Logistic Regression** pada kondisi ketimpangan kelas (*class imbalance*) menggunakan metrik *Precision, Recall, F1-Score, ROC-AUC, Precision-Recall AUC (PR-AUC)*, dan *Balanced Accuracy*, serta mengidentifikasi faktor penyebab utama melalui *feature importance*.
3. Merumuskan dan menyimulasikan metrik **Effective Recall** pada lima skenario jendela waktu pemrosesan (Batch Harian 86.400 detik, Batch Per Jam 3.600 detik, Micro-Batch 300 detik, Near Real-Time 60 detik, dan Near Real-Time 10 detik) serta menguji latensi *end-to-end* pada *micro-batch streaming runner* dengan *trigger* 2 detik.

---

## II. LITERATURE REVIEW

Kajian literatur mengenai analisis *cart abandonment* pada platform e-commerce berakar pada dua ranah penelitian utama: (1) pemodelan perilaku konsumen berbasis *clickstream* dan pembelajaran mesin (*machine learning*), serta (2) arsitektur pemrosesan *Big Data* untuk analitik waktu nyata (*real-time* vs. *batch*).

Pada ranah perilaku konsumen, Kukar-Kinney dan Close [3] menunjukkan bahwa konsumen daring sering menempatkan barang ke dalam keranjang bukan semata-mata untuk membeli saat itu juga, melainkan untuk keperluan riset harga, pengorganisasian belanja, dan hiburan. Rubin et al. [4] serta Zhao et al. [6] memperluas temuan tersebut dengan membuktikan bahwa ragu-ragu pada tahap keranjang (*checkout hesitancy*) sangat dipengaruhi oleh durasi eksplorasi produk, harga relatif terhadap kategori, dan waktu akses. Dalam konteks *clickstream*, Moe [1] dan Montgomery et al. [2] mempelopori pemodelan jalur navigasi (*path analysis*) untuk membedakan pengunjung yang sekadar melihat-lihat (*browsers*) dengan pengunjung yang memiliki niat beli tinggi (*buyers*).

Seiring berkembangnya algoritma pembelajaran mesin, sejumlah peneliti menerapkan model klasifikasi dan *ensemble* untuk memprediksi konversi sesi e-commerce. Baumann et al. [7] dan Cirqueira et al. [11] mengevaluasi berbagai algoritma *supervised learning* pada data log sesi untuk memprediksi *customer purchase intent* dan *cart abandonment*, serta menemukan bahwa algoritma berbasis pohon keputusan (*tree-based ensembles* seperti *Random Forest* dan *Gradient Boosting*) mengungguli model linear karena mampu menangkap interaksi non-linear antara frekuensi klik, variasi item, dan atribut harga. Selain itu, Saito dan Rehmsmeier [12] menegaskan bahwa pada dataset dengan ketimpangan kelas (*imbalanced dataset*), kurva *Precision-Recall* (PR-AUC) memberikan gambaran kinerja yang jauh lebih akurat dibandingkan ROC-AUC semata. Meskipun demikian, studi-studi prediksi clickstream seperti pada [5], [10], dan [11] umumnya mengekstraksi fitur agregat dari keseluruhan sesi (misalnya total durasi sesi penuh atau total halaman hingga pengguna keluar) yang secara praktis belum tersedia ketika pengguna baru saja menekan tombol *add-to-cart*.

Pada ranah arsitektur *Big Data*, Marz dan Warren [8] memperkenalkan **Lambda Architecture** yang memisahkan jalur pemrosesan menjadi *batch layer* (untuk akurasi historis dan pelatihan ulang model di atas *data lake* bervolume besar) dan *speed layer* (untuk inferensi berlatensi rendah). Armbrust et al. [9] melalui *Structured Streaming* menunjukkan bahwa pemrosesan aliran data berbasis *micro-batch* mampu menekan latensi *end-to-end* hingga skala detik sembari mempertahankan konsistensi *fault-tolerance*. Sejumlah penelitian terkini telah mengkaji penerapan arsitektur streaming untuk deteksi anomali dan rekomendasi e-commerce [2], [10], tetapi belum mengaitkan secara kuantitatif bagaimana ukuran jendela pemrosesan (*window size*) menggerus proporsi *True Positive* yang berhasil diputuskan sebelum batas waktu intervensi sesi berakhir.

Berdasarkan sintesis literatur di atas, **kesenjangan penelitian (*research gap*)** yang dijawab oleh studi ini adalah: (1) belum adanya pemodelan *cart abandonment* pada dataset Retailrocket yang menerapkan titik potong observasi dini (*first add-to-cart*) dengan aturan *anti-leakage* lintas sesi yang ketat, dan (2) belum adanya evaluasi terpadu yang mengukur degradasi *Effective Recall* dari arsitektur *batch* harian/jam menuju *micro-batch/near real-time*.

---

## III. RESEARCH METHOD

Tahapan penelitian ini dirancang secara sistematis agar dapat direproduksi sepenuhnya (*reproducible*), mencakup konfigurasi lingkungan komputasi, akuisisi dan *session-ization* data, rekayasa fitur *anti-leakage*, pelatihan dan evaluasi model pada kondisi *class imbalance*, serta simulasi latensi arsitektur *batch* vs. *near real-time*.

### *A. Experimental Environment and Dataset Description*
Seluruh eksperimen pemrosesan data, pelatihan model, dan pengujian *micro-batch streaming* dieksekusi secara lokal pada lingkungan perangkat keras dan perangkat lunak dengan spesifikasi terukur: prosesor **12th Gen Intel(R) Core(TM) i5-12450HX** (8 *physical cores*, 12 *logical threads*), kapasitas memori utama **11,78 GB RAM**, sistem operasi **Windows 10 (Build 26300)**, serta lingkungan terisolasi **Python 3.11.9** (`pandas` 3.1.1, `numpy` 2.4.6, `scikit-learn` 1.9.1, dan `matplotlib` 3.11.2). Pencatatan spesifikasi ini memastikan bahwa pengukuran waktu pelatihan (*training time*) dan latensi inferensi per baris (*inference latency in milliseconds*) memiliki tolok ukur (*baseline*) yang objektif.

Dataset yang digunakan adalah **Retailrocket E-Commerce Dataset**, yaitu kumpulan data *clickstream* dunia nyata yang dikumpulkan selama periode 4,5 bulan (3 Mei 2015 pukul 03:00:04 UTC hingga 18 September 2015 pukul 02:59:47 UTC). Dataset ini terdiri atas tiga komponen utama:
1. **`events.csv`:** Berisi **2.756.101** rekaman interaksi dari **1.407.580** pengunjung unik (`visitorid`) terhadap **235.061** produk unik (`itemid`), yang terbagi atas 2.664.312 aktivitas *view* (96,67%), 69.332 aktivitas *addtocart* (2,52%), dan 22.457 aktivitas *transaction* (0,81%).
2. **`item_properties_part1.csv` & `item_properties_part2.csv`:** Berisi **20.275.902** baris atribut produk lintas waktu untuk **417.053** item unik. Dari tabel bervolume besar ini, diekstraksi dua properti kunci: `categoryid` (kategori produk) dan properti `790` (harga produk yang telah dinormalisasi dengan awalan karakter `n`).
3. **`category_tree.csv`:** Berisi **1.669** relasi hierarki kategori (`categoryid` dan `parentid`).

### *B. Session-ization and Target Labeling*
Karena data mentah `events.csv` tidak menyediakan pengenal sesi (`session_id`), langkah pertama dalam pipeline adalah melakukan *session-ization*. Rekaman diurutkan secara menaik berdasarkan `visitorid` dan waktu kejadian dalam detik (`ts = timestamp // 1000`). Mengikuti standar de facto analitik web [2], [5], sebuah sesi baru terbentuk apabila terjadi pergantian `visitorid` atau terdapat jeda inaktivitas lebih dari 30 menit ($\text{GAP} = 1.800\text{ detik}$) antara dua aktivitas berurutan dari pengunjung yang sama.

Proses *session-ization* terhadap 2.756.101 event menghasilkan total **1.761.660 sesi**. Mengingat fokus penelitian adalah deteksi *cart abandonment*, populasi target difilter hanya pada sesi yang memiliki sedikitnya satu aktivitas `addtocart`, yaitu sebanyak **43.924 sesi**. Pelabelan target biner didefinisikan sebagai berikut:
- **Abandoned (`abandoned = 1`):** Sesi yang memiliki `addtocart` tetapi tidak memiliki aktivitas `transaction` hingga sesi berakhir (sebanyak **31.992 sesi** atau **72,83%**).
- **Completed (`abandoned = 0`):** Sesi yang memiliki `addtocart` dan berhasil dilanjutkan hingga minimal satu `transaction` dalam sesi yang sama (sebanyak **11.932 sesi** atau **27,17%**).

### *C. Strict Anti-Leakage Feature Engineering and Chronological Split*
Agar model dapat diterapkan untuk intervensi dini di dunia nyata, prediksi harus dilakukan tepat ketika pengguna memasukkan barang pertama ke keranjang. Oleh karena itu, **titik observasi (*observation point*)** ditetapkan pada kejadian `addtocart` pertama di setiap sesi ($t_{\text{cart}}$). Seluruh aktivitas yang terjadi setelah $t_{\text{cart}}$ di dalam sesi tersebut dihapus dari perhitungan fitur untuk mencegah kebocoran informasi masa depan (*intra-session data leakage*).

Sepuluh fitur input diekstraksi pada titik observasi $t_{\text{cart}}$:
1. `n_events_before`: Jumlah total aktivitas dalam sesi hingga `addtocart` pertama.
2. `n_views_before`: Jumlah aktivitas `view` sebelum `addtocart` pertama.
3. `n_unique_items`: Jumlah item unik yang dilihat dalam sesi hingga titik observasi.
4. `n_views_same_item`: Frekuensi pengguna melihat item yang sama sebelum memasukkannya ke keranjang.
5. `elapsed_min`: Durasi waktu (menit) sejak awal sesi ($t_{\text{start}}$) hingga `addtocart` pertama ($t_{\text{cart}}$).
6. `hour`: Jam terjadinya `addtocart` pertama (0–23 UTC).
7. `dow`: Hari dalam minggu saat `addtocart` terjadi (0 = Senin s.d. 6 = Minggu).
8. `price_log`: Transformasi logaritmik $\ln(1 + \text{price})$ dari harga item yang dimasukkan ke keranjang (properti `790`).
9. `cat_freq`: *Frequency encoding* dari `categoryid` produk yang dimasukkan ke keranjang.
10. `prev_sessions`: Jumlah sesi masa lalu dari `visitorid` yang sama yang dihitung menggunakan aturan jendela kumulatif ketat (*strict expanding window*), yaitu hanya menghitung sesi sebelumnya yang telah benar-benar selesai sebelum titik observasi sesi saat ini ($\text{end\_ts}_{\text{prev}} < t_{\text{cart}}$).

Selanjutnya, untuk mencegah *inter-session data leakage*, seluruh 43.924 sesi diurutkan secara kronologis berdasarkan $t_{\text{cart}}$ dan dibagi menjadi **80% data Pelatihan (35.139 sesi; rasio *abandoned* 72,75%)** dan **20% data Pengujian (8.785 sesi; rasio *abandoned* 73,16%)**. Nilai hilang (*missing values*) pada atribut harga dan kategori (masing-masing sebesar 1,18%) diimputasi menggunakan median harga dari data *Training* (`59.268,0`), dan pemetaan frekuensi kategori (`cat_freq`) dihitung murni dari distribusi data *Training*.

### *D. Classification Models and Latency Simulation Formulation*
Kami membandingkan dua algoritma klasifikasi dengan karakteristik komputasi berbeda:
1. **Random Forest (`RF`):** Ensemble 200 pohon keputusan (`n_estimators = 200`), kedalaman maksimum `max_depth = 12`, dan pembobotan kelas `class_weight = "balanced"` untuk menangani rasio kelas 72,83% : 27,17%.
2. **Logistic Regression (`LR`):** Pipeline terstandarisasi (`StandardScaler`) dengan `max_iter = 1000` dan `class_weight = "balanced"` sebagai *baseline* berlatensi sangat rendah.

Mengingat ketimpangan kelas positif yang dominan (73,16% pada data uji), evaluasi tidak hanya menggunakan *Precision, Recall, F1-Score*, dan *ROC-AUC*, tetapi juga menyertakan **PR-AUC (*Precision-Recall Area Under Curve*)** dan **Balanced Accuracy** [12].

Untuk menjembatani evaluasi *Machine Learning* dengan arsitektur *Big Data* (*Lambda Architecture*), kami memodelkan waktu keluarnya keputusan prediksi ($t_{\text{decision}}$) pada ukuran jendela pemrosesan berkala $W \in \{86.400, 3.600, 300, 60, 10\}$ detik dan waktu inferensi per baris $t_{\text{infer}}$ sebagaimana dirumuskan pada (1):

$$t_{\text{decision}} = \left(\left\lfloor \frac{t_{\text{cart}}}{W} \right\rfloor + 1\right) \times W + t_{\text{infer}} \tag{1}$$

Sebuah sesi dianggap masih dapat diintervensi (*reachable*) apabila keputusan prediksi keluar sebelum sesi pengguna berakhir ditambah ambang batas inaktivitas 30 menit ($\text{GAP} = 1.800\text{ detik}$). Dengan demikian, batas waktu intervensi (*deadline*) didefinisikan pada (2):

$$t_{\text{deadline}} = t_{\text{end}} + \text{GAP} \tag{2}$$

Prediksi *True Positive* (sesi aktual *abandoned* yang berhasil ditebak positif oleh model, yaitu $y_i = 1 \land \hat{y}_i = 1$) yang baru selesai diproses melewati $t_{\text{deadline}}$ dianggap gagal diintervensi karena pengguna telah meninggalkan platform. Oleh karena itu, metrik **Effective Recall** dirumuskan secara eksplisit pada (3):

$$\text{Effective Recall} = \frac{\sum_{i=1}^{N_{\text{test}}} \mathbb{I}\left(y_i = 1 \land \hat{y}_i = 1 \land t_{\text{decision}, i} \le t_{\text{deadline}, i}\right)}{\sum_{i=1}^{N_{\text{test}}} \mathbb{I}\left(y_i = 1\right)} \tag{3}$$

di mana $\mathbb{I}(\cdot)$ adalah fungsi indikator bernilai 1 jika kondisi terpenuhi dan 0 jika sebaliknya. Terakhir, untuk memvalidasi latensi *speed layer* secara riil, diimplementasikan pengujian *micro-batch streaming* yang mengirimkan 1.000 rekaman uji dalam 10 berkas *chunk* CSV (masing-masing 100 baris dengan penulisan atomik `os.replace`) dan memprosesnya setiap *trigger* 2 detik untuk mengukur distribusi latensi *end-to-end* sejak data ditulis (`write_ts`) hingga inferensi selesai.

---

## IV. RESULTS AND DISCUSSION

### *A. Descriptive Statistics and Behavioral Characteristics*
Dari total 1.761.660 sesi yang terbentuk melalui *session-ization* berambang 30 menit, hanya 43.924 sesi (2,49%) yang mencapai tahap penambahan produk ke keranjang (`addtocart`). Di antara 43.924 sesi keranjang tersebut, 31.992 sesi (72,83%) berakhir sebagai *cart abandonment* dan hanya 11.932 sesi (27,17%) yang berlanjut hingga transaksi selesai. Pada data pengujian (8.785 sesi), median sisa waktu sesi setelah `addtocart` pertama ($t_{\text{end}} - t_{\text{cart}}$) sangat singkat, yakni hanya **85,0 detik** (rata-rata **551,72 detik** atau ±9,2 menit). Fakta empiris ini menjelaskan mengapa kecepatan deteksi sangat krusial: jendela waktu keberadaan pengguna di platform pasca-*add-to-cart* umumnya kurang dari 40 menit termasuk masa tunggu *idle* 30 menit.

Perbandingan rata-rata fitur antara sesi yang berhasil menyelesaikan transaksi (*completed*) dan sesi yang meninggalkan keranjang (*abandoned*) memperlihatkan perbedaan perilaku yang mencolok:
- Pengunjung yang menyelesaikan transaksi memiliki rata-rata riwayat sesi masa lalu (`prev_sessions`) jauh lebih tinggi (**9,44 sesi**) dibandingkan pengunjung yang meninggalkan keranjang (**2,20 sesi**). Hal ini menunjukkan bahwa pelanggan berulang (*returning/loyal visitors*) memiliki kepastian beli yang jauh lebih kuat daripada pengunjung baru.
- Sesi yang berakhir transaksi memiliki durasi eksplorasi sebelum `addtocart` (`elapsed_min`) rata-rata **8,89 menit** dengan **3,76 event** awal, sedangkan sesi *abandoned* rata-rata hanya menghabiskan **4,26 menit** dengan **2,72 event** sebelum memasukkan barang ke keranjang. Ini mengonfirmasi hipotesis bahwa tindakan memasukkan barang ke keranjang secara tergesa-gesa di awal sesi sering kali berfungsi sebagai *bookmark* atau perbandingan harga sementara, bukan niat menyelesaikan pembayaran.

### *B. Classification Performance and Imbalance Evaluation*
Perbandingan kinerja model **Random Forest** dan **Logistic Regression** pada 8.785 sesi data uji menggunakan ambang probabilitas standar ($\tau = 0,50$) disajikan pada Tabel I.

<p align="center">TABLE I<br>COMPARISON OF CLASSIFICATION PERFORMANCE ON CHRONOLOGICAL TEST SET (8,785 SESSIONS)</p>

| Model | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Balanced Acc | Train Time (s) | Infer Latency (ms/row) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | **0.8175** | 0.7095 | 0.7597 | **0.7030** | **0.8574** | **0.6389** | 1.0011 | 0.006635 |
| **Logistic Regression** | 0.8036 | **0.7487** | **0.7752** | 0.6829 | 0.8420 | 0.6250 | **0.0479** | **0.000228** |

Berdasarkan Tabel I, **Random Forest** mengungguli Logistic Regression pada seluruh metrik diskriminasi yang tidak bergantung pada satu titik ambang sekaligus metrik ketimpangan kelas, yaitu **ROC-AUC (0,7030 vs. 0,6829)**, **PR-AUC (0,8574 vs. 0,8420)**, **Balanced Accuracy (0,6389 vs. 0,6250)**, dan **Precision (0,8175 vs. 0,8036)**. Tingginya nilai PR-AUC (0,8574) membuktikan bahwa meskipun kelas positif (*abandoned*) mendominasi 73,16% populasi uji, Random Forest mampu menjaga presisi prediksi positif secara konsisten di berbagai tingkat *recall*. Pada konfigurasi $\tau = 0,50$, Random Forest menghasilkan 4.560 *True Positive*, 1.340 *True Negative*, 1.018 *False Positive*, dan 1.867 *False Negative*.

Di sisi lain, **Logistic Regression** menghasilkan *Recall* sedikit lebih tinggi pada $\tau = 0,50$ (0,7487) yang mendorong *F1-Score* ke 0,7752, serta memiliki waktu pelatihan 20 kali lebih cepat (0,0479 detik vs. 1,0011 detik) dan waktu inferensi per baris 29 kali lebih singkat (0,000228 ms vs. 0,006635 ms). Namun, bahkan pada Random Forest sekalipun, waktu inferensi sebesar **0,006635 ms/baris** berarti sistem mampu memproses sekitar 150.000 prediksi per detik pada satu mesin prosesor Intel Core i5-12450HX, sehingga tambahan beban komputasi Random Forest sama sekali tidak menjadi penghambat (*bottleneck*) pada arsitektur *near real-time*.

Untuk mengevaluasi dampak pergeseran ambang keputusan ($\tau$) terhadap *trade-off* biaya promosi (*Precision*) dan cakupan deteksi (*Recall*), hasil analisis sensitivitas disajikan pada Tabel II.

<p align="center">TABLE II<br>THRESHOLD SENSITIVITY ANALYSIS FOR RANDOM FOREST AND LOGISTIC REGRESSION</p>

| Model | Threshold ($\tau$) | Precision | Recall | F1-Score | Balanced Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | 0.30 | 0.7551 | **0.9818** | **0.8536** | 0.5568 |
| **Random Forest** | 0.40 | 0.7751 | 0.9136 | 0.8387 | 0.5955 |
| **Random Forest** | 0.50 | 0.8175 | 0.7095 | 0.7597 | **0.6389** |
| **Random Forest** | 0.60 | 0.8771 | 0.4176 | 0.5658 | 0.6291 |
| **Random Forest** | 0.70 | **0.9055** | 0.2533 | 0.3959 | 0.5906 |
| **Logistic Regression** | 0.30 | 0.7584 | 0.9687 | 0.8508 | 0.5639 |
| **Logistic Regression** | 0.40 | 0.7694 | 0.9225 | 0.8390 | 0.5845 |
| **Logistic Regression** | 0.50 | 0.8036 | 0.7487 | 0.7752 | 0.6250 |
| **Logistic Regression** | 0.60 | 0.8690 | 0.2983 | 0.4441 | 0.5879 |
| **Logistic Regression** | 0.70 | 0.9369 | 0.0300 | 0.0582 | 0.5123 |

Tabel II memperlihatkan implikasi manajerial yang penting:
- Apabila intervensi pemasaran bersifat **biaya mendekati nol** (misalnya menampilkan *pop-up reminder* atau *badge* stok terbatas di layar), menurunkan ambang Random Forest ke $\tau = 0,40$ meningkatkan *Recall* secara drastis menjadi **91,36%** dan *F1-Score* menjadi **0,8387** dengan tetap menjaga *Precision* di angka **77,51%**.
- Sebaliknya, apabila intervensi melibatkan **subsidi margin finansial** (seperti pemberian voucer diskon langsung), penggunaan ambang $\tau = 0,50$ atau $\tau = 0,60$ lebih disarankan karena memaksimalkan *Balanced Accuracy* (0,6389) dan meningkatkan *Precision* hingga **87,71%**, sehingga meminimalkan pemberian diskon sia-sia kepada pengguna yang sebenarnya tetap akan membeli (*False Positive*).

### *C. Key Drivers of Cart Abandonment and Temporal Patterns*
Untuk menjawab pertanyaan analitik mengenai faktor-faktor yang paling menentukan terjadinya *cart abandonment*, bobot *Gini feature importance* dari model Random Forest divisualisasikan pada Gambar 1.

![Fig. 1. Relative Feature Importance of the Random Forest Model](C:/Bafqi/Big Data/outputs/figures/fig1_feature_importance.png)
<p align="center">Fig. 1. Relative feature importance (Gini importance) of the Random Forest model at the first add-to-cart observation point.</p>

Sebagaimana ditunjukkan pada Gambar 1, tiga prediktor paling dominan menyumbang lebih dari 51% total daya pisah model:
1. **`prev_sessions` (0,1995):** Riwayat jumlah sesi masa lalu pengunjung merupakan indikator terkuat. Pengunjung tanpa riwayat sesi sebelumnya (`prev_sessions = 0`) memiliki kecenderungan sangat tinggi untuk meninggalkan keranjang.
2. **`elapsed_min` (0,1600):** Durasi sejak awal sesi hingga barang pertama masuk ke keranjang menempati urutan kedua, menangkap perbedaan pola antara pengunjung yang langsung menekan *add-to-cart* secara impulsif dan pengunjung yang telah melakukan eksplorasi matang.
3. **`price_log` (0,1515) dan `cat_freq` (0,1277):** Harga produk dan popularitas kategori menyumbang porsi signifikan berikutnya. Rata-rata `price_log` pada sesi *abandoned* (11,0910) lebih tinggi dibandingkan sesi *completed* (11,0364), mengindikasikan sensitivitas harga saat barang sudah berada di dalam keranjang.
4. **Faktor waktu dan intensitas navigasi:** Jam akses (`hour` = 0,1016) dan frekuensi melihat item yang sama (`n_views_same_item` = 0,0811) memberikan kontribusi menengah, diikuti oleh hari dalam minggu (`dow` = 0,0593) dan metrik agregat klik (`n_events_before`, `n_unique_items`, `n_views_before`).

Distribusi tingkat *cart abandonment* berdasarkan jam dan hari ditampilkan pada Gambar 2.

![Fig. 2. Temporal Cart Abandonment Patterns](C:/Bafqi/Big Data/outputs/figures/fig2_temporal_patterns.png)
<p align="center">Fig. 2. Empirical cart abandonment rates across (a) hours of the day (UTC) and (b) days of the week.</p>

Gambar 2(a) menunjukkan fluktuasi mencolok sepanjang hari: tingkat *abandonment* mencapai titik tertinggi pada rentang pukul **08:00–12:00 UTC** dengan puncak pada pukul **09:00 UTC (85,84%)** dan **12:00 UTC (85,09%)**, sementara titik terendah (konversi transaksi tertinggi) terjadi pada pukul **15:00–19:00 UTC** (terendah pada pukul **15:00 UTC sebesar 64,73%**). Sementara itu, Gambar 2(b) memperlihatkan pola mingguan yang jelas: tingkat *abandonment* meningkat secara bertahap menjelang akhir pekan, mencapai puncaknya pada hari **Sabtu (77,39%)** dan **Minggu (76,55%)**, sedangkan hari kerja pertengahan minggu seperti **Rabu (69,88%)**, **Senin (71,05%)**, dan **Selasa (71,07%)** mencatatkan tingkat penyelesaian transaksi yang lebih baik. Hal ini mengindikasikan perilaku *window shopping* yang lebih tinggi pada akhir pekan.

### *D. Batch vs. Near Real-Time Latency and Effective Recall Evaluation*
Temuan paling krusial dari penelitian ini terletak pada perbandingan efektivitas deteksi ketika model Random Forest yang sama ($\text{Offline Recall} = 0,7095$ pada $\tau = 0,50$) dijalankan di bawah lima skenario jendela pemrosesan arsitektur yang berbeda, sebagaimana dirangkum pada Tabel III dan divisualisasikan pada Gambar 3.

<p align="center">TABLE III<br>SIMULATION OF PROCESSING LATENCY AND EFFECTIVE RECALL ACROSS ARCHITECTURAL WINDOWS</p>

| Processing Mode | Window $W$ (s) | Mean Latency (s) | Median Latency (s) | Decided Before Deadline (%) | Timely TP Count | Effective Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Batch Harian (24 Jam)** | 86,400 | 37,343.62 | 26,765.00 | 3.60% | 113 / 6,427 | **0.0176** |
| **Batch Per Jam (1 Jam)** | 3,600 | 1,792.34 | 1,788.00 | 60.47% | 2,512 / 6,427 | **0.3909** |
| **Micro-Batch (5 Menit)** | 300 | 150.21 | 149.00 | **100.00%** | **4,560 / 6,427** | **0.7095** |
| **Near Real-Time (1 Menit)** | 60 | 30.51 | 30.00 | **100.00%** | **4,560 / 6,427** | **0.7095** |
| **Near Real-Time (10 Detik)** | 10 | 5.52 | 5.00 | **100.00%** | **4,560 / 6,427** | **0.7095** |

![Fig. 3. Effective Recall and Timely Decisions Across Architectural Windows](C:/Bafqi/Big Data/outputs/figures/fig3_latency_effective_recall.png)
<p align="center">Fig. 3. Comparison of Effective Recall (%) and percentage of decisions completed before the session intervention deadline across five processing windows.</p>

Data pada Tabel III dan Gambar 3 membuktikan secara kuantitatif bagaimana keterlambatan arsitektur memusnahkan nilai guna model *Machine Learning*:
1. **Kegagalan Operasional Batch Harian ($W = 86.400\text{ detik}$):** Rata-rata latensi mencapai 37.343,62 detik (±10,37 jam). Hanya **3,60%** sesi yang keputusannya keluar sebelum batas waktu intervensi ($t_{\text{end}} + 30\text{ menit}$). Akibatnya, dari 4.560 sesi *abandoned* yang sebenarnya berhasil diprediksi benar oleh Random Forest, hanya **113 sesi** yang terdeteksi tepat waktu, menjatuhkan **Effective Recall dari 0,7095 menjadi 0,0176 (kehilangan 97,5% potensi intervensi)**.
2. **Degradasi Signifikan pada Batch Per Jam ($W = 3.600\text{ detik}$):** Dengan rata-rata latensi tunggu ±29,87 menit (1.792,34 detik), sebanyak 39,53% sesi telah melewati batas intervensi ketika jadwal *batch* dieksekusi. Hal ini menyebabkan **Effective Recall menyusut hampir separuhnya menjadi 0,3909** (hanya 2.512 dari 6.427 sesi *abandoned* yang dapat diintervensi tepat waktu).
3. **Optimalitas Micro-Batch ($\le 300\text{ detik}$) dan Near Real-Time ($60\text{ detik}$ & $10\text{ detik}$):** Ketika jendela pemrosesan diperkecil menjadi 5 menit (300 detik) atau lebih cepat, **100% keputusan prediksi selesai sebelum batas waktu intervensi**, sehingga **Effective Recall tetap utuh sebesar 0,7095** (4.560 sesi). Penurunan jendela ke 60 detik dan 10 detik lebih lanjut memangkas median waktu tunggu keputusan dari 149,0 detik menjadi **30,0 detik** dan **5,0 detik**, yang sangat krusial untuk menangkap pengguna *flash sale* yang masih aktif melihat layar sebelum beralih tab.

Untuk memverifikasi performa aktual *speed layer* dalam mengeksekusi aliran data berkesinambungan, hasil pengujian *micro-batch streaming* terhadap 1.000 sesi uji (10 berkas *chunk* atomik, *trigger* 2 detik) disajikan pada Tabel IV.

<p align="center">TABLE IV<br>END-TO-END LATENCY DISTRIBUTION OF MICRO-BATCH STREAMING BENCHMARK (1,000 STREAMED SESSIONS, 2-SECOND TRIGGER)</p>

| Metric | Value |
| :--- | :---: |
| Streaming Execution Mode | Micro-Batch File Streaming (Atomic Rename, 2s Trigger) |
| Total Streamed Sessions / Micro-Batches | 1,000 rows across 7 active micro-batches |
| Mean End-to-End Latency (s) | **1.2735 s** |
| Standard Deviation Latency (s) | 0.6053 s |
| Minimum Latency (s) | 0.4980 s |
| 25th Percentile ($P_{25}$) Latency (s) | 0.5571 s |
| Median ($P_{50}$) Latency (s) | **1.2596 s** |
| 75th Percentile ($P_{75}$) Latency (s) | 2.0006 s |
| Maximum Latency (s) | **2.0766 s** |
| Mean Batch Model Inference Time (ms) | 28.9815 ms |

Sebagaimana terlihat pada Tabel IV, pipeline *micro-batch streaming* dengan *trigger* 2 detik mencapai rata-rata latensi *end-to-end* (sejak berkas *event* ditulis oleh *producer* hingga prediksi probabilitas Random Forest selesai dihitung) sebesar **1,2735 detik** (median **1,2596 detik**, maksimum **2,0766 detik**), di mana waktu inferensi model untuk satu *batch* berisi ratusan baris hanya memakan rata-rata **28,98 ms**. Hal ini membuktikan bahwa penggabungan model *Random Forest* yang dilatih pada *batch layer* dengan eksekusi inferensi pada *speed layer* ber-trigger 2 detik sepenuhnya layak dioperasikan untuk intervensi *real-time*.

### *E. Study Limitations*
Agar interpretasi temuan tetap objektif dan transparan secara ilmiah, terdapat empat keterbatasan metodologis dalam penelitian ini yang perlu dicatat:
1. **Asumsi Batas Waktu Intervensi (*Deadline* 30 Menit):** Batas waktu efektivitas intervensi ($t_{\text{end}} + 30\text{ menit}$) merupakan asumsi analitis yang diturunkan dari definisi ambang inaktivitas sesi standar. Pada implementasi produksi, jendela respons aktual dapat bervariasi bergantung pada kanal komunikasi yang digunakan (misalnya *in-app pop-up* membutuhkan respons dalam hitungan detik saat sesi masih berlangsung, sedangkan *email/WhatsApp retargeting* masih efektif beberapa menit setelah sesi tertutup).
2. **Resolusi Temporal Atribut Produk (`item_properties`):** Nilai harga (`790`) dan kategori (`categoryid`) diambil menggunakan rekaman terakhir yang tercatat per `itemid` untuk efisiensi penggabungan tabel bervolume 20,27 juta baris, bukan melalui *point-in-time join* pada milidetik setiap event.
3. **Cakupan Dataset Tunggal:** Eksperimen menggunakan satu dataset ritel daring (Retailrocket) dalam rentang waktu 4,5 bulan dengan ID dan nilai harga yang telah dianonimkan/ditransformasi oleh penyedia data.
4. **Simulasi *Streaming* Berbasis Berkas Lokal:** Pengujian *streaming* dilakukan menggunakan *atomic file-based micro-batching* pada satu node komputasi lokal, bukan di atas klaster terdistribusi multi-broker Apache Kafka dan klaster Spark produksi.

---

## V. CONCLUSION

Penelitian ini berhasil merancang, mengimplementasikan, dan mengevaluasi pipeline deteksi dini *cart abandonment* berbasis *Big Data* pada dataset clickstream Retailrocket (2.756.101 event; 43.924 sesi keranjang belanja dengan tingkat *abandonment* 72,83%). Dengan menerapkan aturan *anti-leakage* yang ketat pada titik observasi `addtocart` pertama dan pembagian data kronologis 80:20, model **Random Forest** terbukti memberikan kinerja diskriminasi terbaik dengan **Precision 0,8175, ROC-AUC 0,7030, PR-AUC 0,8574, dan Balanced Accuracy 0,6389**, serta kecepatan inferensi **0,006635 ms/baris**. Analisis *feature importance* mengungkap bahwa jumlah riwayat sesi pengunjung sebelumnya (`prev_sessions` = 0,1995), durasi eksplorasi menuju keranjang (`elapsed_min` = 0,1600), dan logaritma harga produk (`price_log` = 0,1515) merupakan determinan utama yang membedakan pembeli serius dari pelaku *cart abandonment*.

Lebih jauh, evaluasi arsitektur membuktikan bahwa keunggulan akurasi model secara *offline* menjadi tidak bermakna apabila dijalankan di atas pemrosesan *batch* berjendela lebar: **Batch Harian (24 jam)** menjatuhkan *Effective Recall* hingga **0,0176** (hanya 3,60% sesi yang terdeteksi sebelum batas waktu intervensi), dan **Batch Per Jam (1 jam)** menurunkan *Effective Recall* menjadi **0,3909** (60,47% tepat waktu). Sebaliknya, peralihan ke arsitektur **Micro-Batch (5 menit)** dan **Near Real-Time Streaming (10–60 detik)** berhasil mempertahankan **100% keputusan sebelum batas waktu** dengan **Effective Recall penuh sebesar 0,7095**, serta latensi *end-to-end* rata-rata **1,2735 detik** pada pengujian *streaming* ber-trigger 2 detik. Temuan ini mengukuhkan pentingnya penerapan *Lambda Architecture* pada platform e-commerce, di mana *batch layer* dimanfaatkan untuk pelatihan model historis dan *speed layer* digunakan untuk mengeksekusi intervensi retensi keranjang belanja secara instan.

---

## ACKNOWLEDGMENT

Para penulis mengucapkan terima kasih kepada tim pengampu mata kuliah Teknologi Big Data di Sekolah Vokasi Institut Pertanian Bogor (IPB University) atas bimbingan metodologis serta fasilitasi praktikum selama pelaksanaan penelitian ini.

---

## REFERENCES

[1] W. W. Moe, “Buying, searching, or browsing: Differentiating between online shoppers using in-store navigational clickstream,” *Journal of Consumer Psychology*, vol. 13, no. 1–2, pp. 29–39, 2003.  
[2] A. L. Montgomery, S. Li, K. Srinivasan, and J. C. Liechty, “Modeling online browsing and path analysis using clickstream data,” *Marketing Science*, vol. 23, no. 4, pp. 579–595, 2004.  
[3] M. Kukar-Kinney and A. G. Close, “The determinants of consumers’ online shopping cart abandonment,” *Journal of the Academy of Marketing Science*, vol. 38, no. 2, pp. 240–250, 2010.  
[4] D. Rubin, C. Martins, V. Ilyuk, and L. Hildebrand, “The effects of perceived diagnosticity on online shopping cart abandonment,” *Journal of Retailing and Consumer Services*, vol. 52, p. 101911, 2020.  
[5] H. Tang, D. Liao, and Z. Sun, “Predicting shopping cart abandonment with deep sequence models on e-commerce clickstream data,” *IEEE Access*, vol. 8, pp. 134512–134523, 2020.  
[6] H. Zhao, S. Wang, and Y. Chen, “Understanding mobile shopping cart abandonment: An integration of behavioral and contextual factors,” *Electronic Commerce Research and Applications*, vol. 46, p. 101032, 2021.  
[7] A. Baumann, J. Haupt, F. Gebert, and S. Lessmann, “Changing perspectives: Using graph metrics to predict purchase probabilities in e-commerce,” *Expert Systems with Applications*, vol. 94, pp. 137–148, 2018.  
[8] N. Marz and J. Warren, *Big Data: Principles and Best Practices of Scalable Real-Time Data Systems*. Shelter Island, NY, USA: Manning Publications, 2015.  
[9] M. Armbrust, T. Das, J. Torres, B. Yavuz, S. Zhu, R. Xin, A. Ghodsi, I. Stoica, and M. Zaharia, “Structured streaming: A declarative API for real-time applications in Apache Spark,” in *Proc. ACM SIGMOD Int. Conf. Management of Data*, Houston, TX, USA, 2018, pp. 601–613.  
[10] M. Sakar, S. O. Polat, M. Katircioglu, and Y. Kastro, “Real-time prediction of online shoppers’ purchasing intention using multilayer perceptron and LSTM recurrent neural networks,” *Neural Computing and Applications*, vol. 31, no. 10, pp. 6893–6908, 2019.  
[11] D. Cirqueira, M. Hofer, D. Nedbal, M. Helfert, and M. Bezbradica, “Customer purchase behavior prediction in e-commerce: A conceptual framework and research agenda,” in *Proc. Int. Workshop New Frontiers in Mining Complex Patterns (NFMCP)*, Cham, Switzerland: Springer, 2020, pp. 119–136.  
[12] T. Saito and M. Rehmsmeier, “The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets,” *PLOS ONE*, vol. 10, no. 3, p. e0118432, 2015.  
