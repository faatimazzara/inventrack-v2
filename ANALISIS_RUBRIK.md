# Laporan Analisis Proyek 1a — InvenTrack v2.0

**Skenario A: Sistem Manajemen Inventaris Produk E-Commerce**  
**Fokus:** Insert · Search by ID · Delete · ADT · Array-based List · Linked List · Hash Table

> Isian ini disusun sebagai dasar laporan. **Link GitHub, link video, dan angka waktu pengukuran harus diisi dari hasil sebenarnya.** Jangan menulis hasil benchmark sebagai angka pasti sebelum menjalankan pengukuran di laptop.

## 1. Karakteristik data dan kebutuhan operasi

Data inventaris berupa produk dengan ID unik; jumlahnya berpotensi besar, terus bertambah, diubah, dan dihapus. Pendaftaran produk harus menolak ID duplikat. Pencarian pelanggan menargetkan ID yang tepat, bukan pencarian indeks atau teks sebagian. Produk yang ditarik harus dihapus berdasarkan ID. Ketiga operasi tersebut berlangsung dengan frekuensi tinggi, sehingga biaya pencarian linear akan semakin terasa saat n meningkat. Selain kecepatan, sistem perlu validasi harga/stok serta pelacakan transaksi. Hash Table menjadi kandidat kuat karena akses menurut key.

Kebutuhan inti dipisahkan dari fitur tambahan: **insert, search(ID), delete(ID)** merupakan inti rubrik; pengaturan akun, stok, laporan, dan audit adalah penguat OOP serta demonstrasi operasional.

## 2. Data yang dioperasikan: kelas, atribut, dan operasi

| Kelas | Atribut utama | Method/operasi |
|---|---|---|
| `Product` | `product_id`, `name`, `category`, `brand`, `price`, `stock`, `minimum_stock`, `description`, `created_at`, `updated_at` | `change`, `to_dict`, `from_dict`, `inventory_value`, `stock_status` |
| `User` | `username`, `full_name`, `role`, `password_hash`, `active` | `to_dict`, `from_dict`, `public_dict` |
| `StockTransaction` | `transaction_id`, `product_id`, `movement_type`, `before`, `after`, `quantity`, `reason`, `actor`, `timestamp` | `create`, `to_dict`, `from_dict` |
| `AuditEvent` | `event_id`, `actor`, `action`, `details`, `timestamp` | `create`, `to_dict`, `from_dict` |
| `InventoryRepository (ADT)` | Antarmuka abstrak | `insert`, `search`, `update`, `delete`, `all`, `__len__` |
| `ArrayRepository` | `_items` (`list`) | Implementasi operasi ADT berbasis list |
| `LinkedRepository` | `_head`, `_tail`, `_size` dan `Node(value,next)` | Implementasi operasi ADT berbasis pointer |
| `HashRepository` | `_data` (`dict`) | Implementasi operasi ADT berbasis key ID |
| `ProductService` | `repo`, `access`, `audit` | `add`, `get`, `update`, `delete`, `list_all` |
| `StockService` | `repo`, `access`, `audit`, `_transactions` | `move`, `adjust`, `history`, `load` |
| `SearchService` | `repo`, `access` | `find` dengan nama/kategori/harga/status |
| `ReportService` | `repo`, `access` | `summary`, `category_values` |
| `AuditService` | `access`, `_events` | `record`, `list_events`, `load` |
| `AuthService` | `users`, `access` | `bootstrap_admin`, `login`, `add_user`, `change_role`, `set_active`, `reset_password`, `change_own_password` |
| `BenchmarkRunner` | Tiga implementasi repository | `run` untuk insert, search berhasil, search gagal, delete |

## 3. Struktur data yang digunakan dan alasan pemilihannya

| Struktur data | Digunakan pada | Alasan |
|---|---|---|
| **Hash Table (`dict`)** | `HashRepository._data` sebagai penyimpan produk utama; `UserStore._users` sebagai indeks akun | Produk dan pengguna memiliki key unik. `insert/search/delete` berdasarkan key rata-rata O(1). Cocok untuk operasi ID berulang pada skala data besar. |
| **Array-based List (`list`)** | `ArrayRepository._items`, daftar transaksi/audit, keluaran laporan, data benchmark | Sederhana dan terurut, iterasi dan append efektif; tetapi mencari/menghapus produk berdasarkan ID perlu O(n). |
| **Custom Singly Linked List** | `LinkedRepository` dan class `Node` untuk perbandingan | Demonstrasi ADT dan akses menggunakan node/pointer; operasi berdasarkan ID harus traversal O(n). |
| **Tuple** | Paket argumen konfigurasi benchmark | Mengelompokkan parameter tetap; ini pendukung, bukan struktur yang menjadi fokus perbandingan. |

> Tiga kandidat yang **dinilai** adalah list, linked list, dan dict. Tidak ada keharusan menambahkan struktur lain hanya untuk memperbanyak jenis ADT.

## 4. Perbandingan Big-O

Dengan n = jumlah produk:

| Operasi | `list` | Singly Linked List | `dict` |
|---|---|---|---|
| Insert **dengan pemeriksaan ID unik** | O(n) | O(n) | rata-rata O(1), worst O(n) |
| Search ID berhasil | best O(1), average O(n), worst O(n) | best O(1), average O(n), worst O(n) | average O(1), worst O(n) |
| Search ID gagal | O(n) | O(n) | average O(1), worst O(n) |
| Delete berdasarkan ID | O(n) | O(n) | average O(1), worst O(n) |
| Update berdasarkan ID | O(n) | O(n) | average O(1), worst O(n) |
| Membaca seluruh koleksi | O(n) | O(n) | O(n) |
| Kompleksitas ruang | O(n) | O(n) + overhead node/pointer | O(n) + overhead tabel |

**Pembuktian intuitif:** Pada list/linked list, tiap elemen bisa memiliki ID target sehingga perlu dibandingkan satu per satu (hingga n perbandingan). Pada hash table, nilai hash ID menunjukkan lokasi pencarian sehingga rata-rata tidak bergantung langsung pada panjang koleksi. Collision/resize menyebabkan kasus terburuk lebih tinggi.

## 5. Analisis pergantian struktur data pada operasi 1

| Operasi | Struktur sebelum | Struktur sesudah | Hasil analisis teoritis |
|---|---|---|---|
| **Search produk berdasarkan ID** | `ArrayRepository (list)` | `HashRepository (dict)` | Pencarian linear O(n) berubah menjadi rata-rata O(1). Untuk n besar dan pencarian sering, diperkirakan hash lebih baik; nilai waktunya harus diuji. |

**Percobaan nyata:** Login Developer → Benchmark → `search berhasil`, lalu `search gagal`. Gunakan ukuran identik dan pengulangan. Bandingkan **median nanodetik per operasi** dari hasil yang dihasilkan program. Angka laptopmu diisi dari CSV `outputs/benchmark.csv`, bukan dari contoh ini.

| Ukuran n | Median `list` (ns/op) | Median `dict` (ns/op) | Interpretasi hasil sebenarnya |
|---|---|---|---|
| 100 | *(isi dari CSV)* | *(isi dari CSV)* | *(setelah pengujian)* |
| 500 | *(isi dari CSV)* | *(isi dari CSV)* | *(setelah pengujian)* |
| 1000 | *(isi dari CSV)* | *(isi dari CSV)* | *(setelah pengujian)* |

## 6. Analisis pergantian struktur data pada operasi lain

| Operasi | Struktur sebelum | Struktur sesudah | Hasil analisis teoritis |
|---|---|---|---|
| **Insert produk baru dengan cek duplikat** | `LinkedRepository` | `HashRepository` | Cek duplikat Linked List O(n) walau append setelah tail O(1). Hash rata-rata O(1), sehingga lebih sesuai untuk input produk terus-menerus. |
| **Delete produk berdasarkan ID** | `ArrayRepository` | `HashRepository` | List perlu mencari indeks dan mungkin menggeser elemen, O(n). Hash `pop(key)` rata-rata O(1). |
| **Search ID yang tidak ada** | `LinkedRepository` | `HashRepository` | Linked List harus melewati seluruh n node, O(n). Dict rata-rata O(1). |

Jika ingin membandingkan Linked List dengan List secara terpisah, gunakan hasil seluruh benchmark, bukan sekadar kesimpulan teori. Semua struktur memakai **urutan operasi dan data yang sama**.

## 7. Simulasi singkat

Koleksi awal: PRD001, PRD002, PRD003. Pencarian/hapus berdasarkan ID **PRD002**.

- **List**: `[(P001), (P002), (P003)]` → scan hingga indeks 1 → `pop(1)` → P003 bergeser ke kiri.
- **Linked List**: `HEAD -> P001 -> P002 -> P003 -> None` → cari node P002 → node P001 diarahkan ke node P003.
- **Hash Table**: `{'P001': ..., 'P002': ..., 'P003': ...}` → lookup `['P002']` → `pop('P002')`.

## 8. Evaluasi hasil pengukuran

`benchmark_runner.py` mengukur durasi pada bagian operasi, menggunakan `time.perf_counter_ns()`, mengulang pengujian, dan menghitung median serta rata-rata **per operasi**. Setup, pembuatan data, dan ekspor tidak ikut dihitung. Pada eksperimen skala kecil hasil mungkin berubah karena cache, proses OS, biaya interpreter, dan variasi mesin. Tren hasil dan Big-O harus dibahas terpisah. Ada biaya pemeriksaan untuk memastikan pencarian berhasil/gagal di dalam loop yang sama pada seluruh struktur; hasil tetap *benchmark implementasi program*.

**Keterbatasan:** Hash table O(1) adalah kompleksitas **di memori**, bukan jaminan seluruh penyimpanan JSON (penulisan snapshot O(n)). Prototipe akademis belum memakai database untuk konkurensi atau puluhan juta produk, sehingga klaim performa skala produksi tidak boleh dibuat.

## 9. Kesimpulan

Hash Table (`dict`) menjadi pilihan paling tepat untuk **penambahan, pencarian, dan penghapusan produk berdasarkan ID** karena ketiga operasi memiliki kompleksitas rata-rata O(1). Array-based List dan custom Singly Linked List tetap penting sebagai pembanding dan bukti penguasaan ADT, tetapi keduanya memerlukan pencarian ID O(n) untuk menjalankan operasi secara utuh. Analisis ini menghubungkan karakteristik inventaris, kompleksitas operasi, trade-off memori, dan pengukuran waktu nyata.

## 10. Bukti pengumpulan

- **Link repositori GitHub:** *(isi setelah diunggah)*
- **Link video presentasi durasi 5–15 menit:** *(isi setelah diunggah)*
- **Bukti output pengujian:** `python -m unittest discover -s tests -v`
- **Bukti benchmark:** CSV asli hasil developer dari `outputs/benchmark.csv`

### Rancangan demonstrasi video (±10–12 menit)

1. 0:00–1:15 — Tujuan, karakteristik data, dan tiga operasi pada skenario.
2. 1:15–3:00 — Jelaskan OOP, ADT `InventoryRepository`, tiga repository dan Big-O.
3. 3:00–6:30 — Login Admin, tambah/cari/hapus produk, validasi duplikasi, stok dan laporan.
4. 6:30–9:30 — Login Developer, simulasi dan benchmark tiga struktur, ekspor CSV.
5. 9:30–11:00 — Simpulan pemilihan Hash Table, trade-off dan keterbatasan.
