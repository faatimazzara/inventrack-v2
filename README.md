# InvenTrack v2.0

**E-Commerce Inventory Management & Data Structure Analysis System**  
Python CLI · OOP · ADT · Multiuser · Role-based access · JSON · Benchmark · Unit Test

## A. Cara menjalankan (Windows / VS Code)

Syarat: **Python 3.10 atau lebih baru**. Tidak perlu `rich`, pip, atau instalasi pustaka tambahan.

1. Ekstrak ZIP sampai terlihat folder `inventrack-v2` berisi `main.py`.
2. Buka folder `inventrack-v2` di VS Code (**File > Open Folder**).
3. Terminal (**Ctrl + `**), jalankan:

   ```powershell
   python main.py
   ```

   Jika Windows menggunakan `py`, gunakan `py -3 main.py`.

4. **Pertama kali**: buat akun Admin Inventaris (username, nama, password minimal 8 karakter), kemudian login.
5. Login admin → **Manajemen akun pengguna** → buat akun `staff`, `manager`, dan `developer` dengan password masing-masing.
6. Pilih **0** pada submenu untuk kembali, dan **0** pada menu utama role untuk logout.

Pengujian otomatis:

```powershell
python -m unittest discover -s tests -v
```

Jalankan dengan data terpisah (berguna untuk pengujian tanpa menyentuh data utama):

```powershell
python main.py --data-dir .\data-demo --output-dir .\hasil-demo
```

**Jangan menjalankan `main.py` menggunakan Python yang berbeda dari interpreter VS Code**, meskipun proyek ini tidak memerlukan pustaka eksternal.

## B. Mode berdasarkan hak akses

| Role | Fitur |
|---|---|
| Admin Inventaris | CRUD produk, stok masuk/keluar/penyesuaian, pencarian, laporan, aktivitas, akun pengguna |
| Staf Gudang | Lihat/cari produk, stok masuk/keluar, stok rendah/habis, riwayat transaksi stok |
| Manajer Inventaris | Pencarian, filter, laporan, stok rendah, riwayat aktivitas (hanya baca) |
| Developer / Tim IT | Analisis karakteristik/kompleksitas, simulasi Array/List/Hash, benchmark, ekspor CSV |

Login memeriksa password dengan PBKDF2-HMAC-SHA256 + salt; role dicek di **service layer**, bukan hanya menu. Akun awal admin dibuat sekali dan tidak ada password bawaan. Ini sistem edukasi lokal, bukan layanan multiuser jaringan.

## C. Fokus skenario tugas (rubrik Proyek 1a)

Perusahaan e-commerce dengan **jutaan produk** membutuhkan: (1) penambahan produk baru; (2) pencarian cepat **berdasarkan ID Produk**; (3) penghapusan produk yang ditarik dari pasar. Dataset besar menjadi dasar *pemilihan algoritma*, bukan klaim bahwa prototipe JSON telah teruji jutaan data.

### 1. Analisis karakteristik data dan operasi — bobot rubrik 20%

- Produk diidentifikasi oleh ID unik, memiliki nama, kategori, merek, harga, stok, batas minimum, dan deskripsi.
- Data tumbuh dan berubah; operasi utama adalah **insert, search(ID), delete(ID)** dengan frekuensi tinggi.
- *Insert* harus menolak ID duplikat, bukan sekadar melakukan append.
- *Search* menggunakan **kecocokan ID penuh**, berbeda dari pencarian nama/kategori yang tetap membutuhkan scan.
- *Delete* menghapus berdasarkan ID, bukan indeks/posisi.
- Kebutuhan integritas: harga dan stok nonnegatif, stok keluar tidak boleh melebihi stok, riwayat dapat ditelusuri.
- Kebutuhan performa: biaya operasi yang tidak meningkat sebanding ukuran data bila memungkinkan; pertimbangkan memori dan worst-case.

### 2. Perbandingan kompleksitas waktu — bobot rubrik 35%

| Operasi **berdasarkan ID** | Array-based List (`list`) | Custom Singly Linked List | Hash Table (`dict`) |
|---|---|---|---|
| Cari ID (berhasil) | best O(1), rata-rata/worst O(n) | best O(1), rata-rata/worst O(n) | rata-rata O(1), worst O(n) |
| Cari ID (tidak ada) | O(n) | O(n) | rata-rata O(1), worst O(n) |
| Tambah produk **dengan cek ID duplikat** | O(n) | O(n) | rata-rata O(1), worst O(n) |
| Hapus berdasarkan ID | O(n) | O(n) | rata-rata O(1), worst O(n) |
| Update berdasarkan ID | O(n) | O(n) | rata-rata O(1), worst O(n) |
| Tampilkan semua produk | O(n) | O(n) | O(n) |
| Penyimpanan elemen | O(n) | O(n) | O(n) |

Penjelasan tepat:

- `list.append()` **sendiri**: O(1) amortisasi, tetapi operasi **menambah produk unik** memerlukan pencarian duplikat terlebih dahulu, sehingga O(n) untuk keseluruhannya.
- Linked List dengan `_tail` dapat menambahkan node pada akhir dalam O(1) **setelah verifikasi**; tanpa indeks tambahan pemeriksaan ID unik O(n). Hapus ID perlu traversal O(n), perubahan pointer setelah node ditemukan O(1).
- Python `dict` mengimplementasikan hash table: `in`, `get`, `pop` O(1) **rata-rata**, bukan jaminan kasus terburuk. Collision dan resizing dapat menimbulkan biaya lebih besar. Worst case dicatat O(n).
- Menampilkan semua data dan memfilter nama/kategori menggunakan traversal O(n), bahkan saat repository utama `dict`.
- Big-O adalah analisis pertumbuhan asimtotik. Waktu nanodetik dari benchmark adalah hasil empiris, tidak boleh disamakan dengan bukti Big-O.

### 3. Pemilihan struktur paling sesuai — bobot rubrik 30%

**Hash Table (`dict`) dipilih** sebagai `HashRepository` karena operasi tambah/cari/hapus dengan kunci ID yang unik menjadi beban kerja utama. Lookup berdasarkan hash rata-rata O(1), sedangkan tanpa indeks Array/Linked List melakukan pencarian linear O(n). Penghematan waktu sangat relevan saat jumlah produk membesar.

**Trade-off**: Hash Table memakai ruang ekstra untuk tabel hash, membutuhkan penanganan collision dan resizing secara internal oleh Python. Urutan fisik data bukan dasar pencarian; untuk filter nama/kategori, scan tetap O(n). Python `list` cocok jika akses indeks/iterasi dominan, sedangkan Linked List cocok untuk pengubahan pointer setelah posisi node diketahui. Untuk skenario pencarian berdasarkan ID, dua pilihan tersebut kalah dalam rata-rata biaya operasi.

### 4. Laporan hasil analisis — bobot rubrik 15%

Analisis dan hasil eksperimen dapat disampaikan berurutan: karakteristik data → definisi operasi → perbandingan Big-O → pilihan struktur → kode ADT → uji fungsional → benchmark → simpulan. Tabel lengkap untuk isian lembar aktivitas tersedia di **`ANALISIS_RUBRIK.md`**.

## D. Penerapan OOP dan ADT

- **Class/object**: `Product`, `User`, `StockTransaction`, `AuditEvent`, berbagai repository/service.
- **Encapsulation**: data domain berupa frozen dataclass, repository menyimpan koleksi privat (`_items`, `_head`, `_data`).
- **Abstraction**: `InventoryRepository(ABC)` mendefinisikan `insert`, `search`, `update`, `delete`, `all`, `__len__`.
- **Inheritance + polymorphism**: `ArrayRepository`, `LinkedRepository`, `HashRepository` menerapkan interface sama. `BenchmarkRunner` memakai ketiganya tanpa mengubah operasi.
- **Composition/dependency injection**: service menerima objek repository dan access control yang dibuat di `bootstrap.py`.
- **Exception handling**: error khusus duplicate/not-found/validation/auth/stock tidak cukup.

Alur: **CLI → Service (+ autentikasi/otorisasi) → InventoryRepository → HashRepository**. Mode developer menjalankan repository pembanding pada dataset sintetis, **tidak memodifikasi inventaris asli**.

## E. Uji benchmark yang dapat direproduksi

1. Login sebagai `developer`.
2. Menu 2 (**Benchmark performa**).
3. Menu 5 (**Semua benchmark**) dengan ukuran `100,500,1000`, 3 kali pengulangan.
4. Menu 6/7 untuk tabel dan analisis, lalu menu 8 untuk ekspor CSV ke `outputs/benchmark.csv`.
5. Hasil menampilkan **median** dan **rata-rata** nanodetik per operasi per struktur per ukuran data.

Dataset dihasilkan terlebih dahulu. Untuk `search` dan `delete`, repository disiapkan di luar timer. Setiap repository menerima **produk dan urutan ID yang identik**; tiap pengulangan menggunakan repository baru. Operasi `search_hit` dan `search_miss` dipisahkan. Setup dan serialisasi CSV tidak masuk ke waktu eksekusi. Waktu tiap mesin dapat berbeda; gunakan tren, bukan sekadar satu angka.

## F. Struktur folder dan penyimpanan

- `inventrack/domain/`: model, validasi, enums, exception.
- `inventrack/adt/` dan `repositories/`: kontrak ADT + tiga implementasi.
- `inventrack/auth/`: autentikasi, hashing, otorisasi.
- `inventrack/services/`: logika produk, stok, pencarian, laporan, audit.
- `inventrack/storage/`: JSON, load, save, berkas akun; snapshot ditulis dengan file sementara lalu rename atomik.
- `inventrack/benchmark/`: dataset, benchmark, analisis.
- `inventrack/cli/menus/`: menu berdasarkan role, setiap submenu memiliki `0. Kembali`.
- `tests/`: pengujian berbasis `unittest` (pustaka standar).

Data lokal tersimpan di `data/users.json` dan `data/inventory.json` setelah mulai menggunakan aplikasi. File akun **jangan diunggah ke GitHub**; `.gitignore` sudah mengecualikan data JSON. Ubah password bila memindahkan instalasi ke perangkat lain.

## G. Bukti tugas untuk dikumpulkan

- Repositori GitHub: unggah seluruh **kode**, README, `ANALISIS_RUBRIK.md`, dan unit test. Hindari `data/*.json` dan `.venv/`.
- Jawaban tabel pada lembar aktivitas: lihat `ANALISIS_RUBRIK.md`.
- Hasil pengukuran **riil**: gunakan CSV yang dihasilkan mesinmu, bukan angka fiktif.
- Presentasi 5–15 menit: tunjukkan skenario, jalankan operasi, jelaskan kontrak ADT dan implementasinya, tampilkan hasil benchmark, tutup dengan justifikasi Hash Table.

## H. Batasan prototipe

CLI berjalan satu proses pada satu komputer; JSON bukan database transaksional atau penyimpanan aman untuk layanan e-commerce nyata. Snapshot inventaris membutuhkan O(n) waktu penulisan, sehingga **O(1) operasi hash di memori tidak berarti seluruh operasi sampai disk O(1)**. Implementasi ini cocok sebagai demonstrasi algoritma dan OOP, bukan sistem produksi jutaan produk bersamaan. Tidak ada jaringan, manajemen sesi lintas perangkat, audit *tamper-proof*, maupun enkripsi data di disk. Penggunaan dataset benchmark maksimal 5.000 melalui CLI untuk menjaga percobaan layak dijalankan pada laptop mahasiswa.
