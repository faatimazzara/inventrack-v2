from inventrack.benchmark.benchmark_analyzer import BIG_O

DATA_CHARACTERISTICS = """KARAKTERISTIK DATA INVENTARIS E-COMMERCE
- Banyak produk (skenario: jutaan), dinamis dan terus bertambah.
- ID produk unik dan stabil; pencarian tepat berdasarkan ID sangat sering.
- Penambahan memerlukan pemeriksaan ID duplikat.
- Penghapusan berdasarkan ID, bukan berdasarkan posisi list.
- Data memiliki atribut nama, kategori, merek, harga, stok, dan waktu.
- Kebutuhan akurasi: ID unik, stok tidak negatif, perubahan dapat diaudit.
- Trade-off: kecepatan akses, penggunaan memori, dan kompleksitas implementasi.
"""

CHOICE_ANALYSIS = """ALASAN MEMILIH HASH TABLE (PYTHON DICT)
Hash Table cocok untuk pemetaan ID Produk -> Product. Dalam kondisi normal,
insert, search, dan delete berdasarkan ID memerlukan O(1) rata-rata. Array
(Python list) dan Singly Linked List perlu penelusuran O(n) agar dapat
menemukan ID dan mencegah duplikasi. Pada linked list, append dapat O(1)
karena ada tail pointer, tetapi pemeriksaan duplikat membuat proses lengkap
O(n). Pada list, append amortisasi O(1), namun pencarian ID tetap O(n).

Worst-case hash table dapat mencapai O(n) akibat tabrakan hash; operasi
resize juga memerlukan waktu tambahan. Hash Table memakai overhead memori
untuk bucket dan pengelolaan tabel. Struktur list/linked list tidak memiliki
indeks hash; linked list punya overhead objek Node dan pointer. Iterasi
seluruh produk dan filter nama/kategori masih O(n) pada implementasi ini.

Kesimpulan: Hash Table (dict) paling tepat sebagai repositori produk utama
berdasarkan frekuensi tinggi operasi ID. Ini tidak berarti semua operasi
menjadi O(1) atau aplikasi prototipe JSON ini siap jutaan produk.
"""


def complexity_table() -> str:
    titles = ("insert", "search_hit", "search_miss", "delete")
    lines = [f"{'Struktur':<22} " + " | ".join(f"{t:<28}" for t in titles)]
    lines.append("-" * 150)
    for repo, times in BIG_O.items():
        lines.append(f"{repo:<22} " + " | ".join(f"{times[t]:<28}" for t in titles))
    return "\n".join(lines)


def operation_walkthrough() -> str:
    return """SIMULASI SINGKAT INSERT, SEARCH, DELETE (BERDASARKAN ID)
Contoh ID: PRD001, PRD002, PRD003. Dicari/dihapus: PRD002.
Array-based List: [PRD001, PRD002, PRD003]; cari dari awal, temukan pada
indeks 1, hapus dengan pop(1), elemen berikutnya bergeser ke kiri.
Singly Linked List: HEAD -> PRD001 -> PRD002 -> PRD003 -> None; telusuri
node, ubah next milik PRD001 ke PRD003 saat PRD002 dihapus.
Hash Table: {PRD001: produk1, PRD002: produk2, PRD003: produk3}; gunakan
lookup kunci PRD002, kemudian pop('PRD002') untuk menghapus.
Semua struktur tetap mengecek ID duplikat ketika menyisipkan produk baru.
"""
