import csv
from pathlib import Path

from inventrack.benchmark.benchmark_runner import BenchmarkResult


BIG_O = {
    "Array-based List": {"insert": "O(n) termasuk cek duplikat", "search_hit": "O(n)",
                         "search_miss": "O(n)", "delete": "O(n)"},
    "Singly Linked List": {"insert": "O(n) termasuk cek duplikat", "search_hit": "O(n)",
                           "search_miss": "O(n)", "delete": "O(n)"},
    "Hash Table (dict)": {"insert": "O(1) rata-rata", "search_hit": "O(1) rata-rata",
                          "search_miss": "O(1) rata-rata", "delete": "O(1) rata-rata"},
}


def format_results(results: list[BenchmarkResult]) -> str:
    header = f"{'Ukuran':>7}  {'Operasi':<13}  {'Struktur':<20} {'Median ns/op':>14} {'Rata-rata ns/op':>16}"
    lines = [header, "-" * len(header)]
    for row in sorted(results, key=lambda r: (r.dataset_size, r.operation, r.repository)):
        lines.append(f"{row.dataset_size:>7}  {row.operation:<13}  "
                     f"{row.repository:<20} {row.median_ns_per_op:>14,.1f} "
                     f"{row.mean_ns_per_op:>16,.1f}")
    return "\n".join(lines)


def interpret(results: list[BenchmarkResult]) -> str:
    if not results:
        return "Belum ada hasil benchmark."
    lines = ["Analisis berdasarkan MEDIAN waktu per operasi (lebih kecil = lebih cepat):"]
    keys = sorted({(r.dataset_size, r.operation) for r in results})
    for size, op in keys:
        group = [r for r in results if r.dataset_size == size and r.operation == op]
        winner = min(group, key=lambda r: r.median_ns_per_op)
        lines.append(f"- n={size}, {op}: {winner.repository} ({winner.median_ns_per_op:,.1f} ns/operasi)")
    lines.append("Catatan: benchmark adalah pengukuran mesin ini, bukan pembuktian Big-O.")
    lines.append("Pembuatan dataset, pengisian awal, dan pembentukan laporan tidak termasuk waktu operasi.")
    return "\n".join(lines)


def export_csv(results: list[BenchmarkResult], path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(BenchmarkResult.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(row.to_dict() for row in results)
    return target
