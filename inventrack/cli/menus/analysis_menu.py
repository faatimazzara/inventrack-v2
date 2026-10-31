from inventrack.benchmark.analysis import (CHOICE_ANALYSIS, DATA_CHARACTERISTICS,
                                           complexity_table, operation_walkthrough)


def run(app) -> None:
    io = app.io
    while True:
        choice = io.menu("LAB ANALISIS STRUKTUR DATA", {
            "1": "Analisis karakteristik data", "2": "Kompleksitas Big-O",
            "3": "Simulasi insert/search/delete", "4": "Alasan memilih Hash Table",
            "5": "Ulasan Array-based List", "6": "Ulasan Singly Linked List",
            "7": "Ulasan Hash Table"})
        if choice == "0":
            return
        passages = {
            "1": DATA_CHARACTERISTICS,
            "2": complexity_table(),
            "3": operation_walkthrough(),
            "4": CHOICE_ANALYSIS,
            "5": ("ARRAY-BASED LIST: index langsung O(1); pencarian ID O(n); "
                  "append O(1) amortisasi; hapus berdasarkan ID O(n). "
                  "Cek duplikat membuat penyisipan lengkap O(n)."),
            "6": ("SINGLY LINKED LIST: setiap elemen disimpan sebagai Node "
                  "(value, next). Pencarian, update, hapus ID O(n). "
                  "Append O(1) dengan tail pointer, tetapi cek duplikat O(n)."),
            "7": ("HASH TABLE (DICT): hash key menentukan lokasi bucket; "
                  "insert/search/delete O(1) rata-rata, O(n) worst-case. "
                  "Ada overhead memori, collision, dan resize. "
                  "Filter nama/kategori tetap O(n)."),
        }
        io.say(passages.get(choice, "Pilihan menu tidak valid."))
