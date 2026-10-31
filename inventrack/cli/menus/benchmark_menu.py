from inventrack.benchmark.benchmark_analyzer import export_csv, format_results, interpret
from inventrack.benchmark.benchmark_runner import BenchmarkRunner


def run(app) -> None:
    io = app.io
    while True:
        choice = io.menu("BENCHMARK STRUKTUR DATA", {
            "1": "Benchmark insert", "2": "Benchmark search berhasil",
            "3": "Benchmark search gagal", "4": "Benchmark delete",
            "5": "Semua benchmark", "6": "Tabel hasil terakhir",
            "7": "Analisis hasil terakhir", "8": "Export hasil CSV"})
        if choice == "0":
            return
        if choice in ("1", "2", "3", "4", "5"):
            def action():
                raw = io.ask("Ukuran data (contoh 100,500,1000; Enter=default): ", required=False)
                sizes = tuple(int(value.strip()) for value in raw.split(",")) if raw else (100, 500, 1000)
                if not sizes or any(not 1 <= value <= 5000 for value in sizes):
                    raise ValueError("Setiap ukuran dataset harus 1 sampai 5.000.")
                raw_repeats = io.ask("Jumlah pengulangan (Enter=3): ", required=False)
                repeats = int(raw_repeats) if raw_repeats else 3
                operations = {"1": ("insert",), "2": ("search_hit",),
                              "3": ("search_miss",), "4": ("delete",),
                              "5": ("insert", "search_hit", "search_miss", "delete")}[choice]
                io.say("Mengukur operasi; data uji dibuat di luar waktu pengukuran...")
                app.benchmark_results = BenchmarkRunner().run(sizes, repeats, operations)
                io.say(format_results(app.benchmark_results))
                io.say("Hasil pengukuran aktual, dapat berbeda antar mesin.")
            app.safe(action)
        elif choice == "6":
            io.say(format_results(app.benchmark_results) if app.benchmark_results
                   else "Belum ada hasil. Jalankan benchmark terlebih dahulu.")
        elif choice == "7":
            io.say(interpret(app.benchmark_results))
        elif choice == "8":
            def action():
                if not app.benchmark_results:
                    io.say("Belum ada hasil untuk diekspor.")
                    return
                path = export_csv(app.benchmark_results, app.output_dir / "benchmark.csv")
                io.say(f"CSV berhasil dibuat: {path}")
            app.safe(action)
        else:
            io.say("Pilihan menu tidak valid.")
