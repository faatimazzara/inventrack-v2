import tempfile
from pathlib import Path
import unittest

from inventrack.benchmark.benchmark_analyzer import export_csv, format_results, interpret
from inventrack.benchmark.benchmark_runner import BenchmarkRunner


class BenchmarkTests(unittest.TestCase):
    def test_small_workload_across_three_structures(self):
        results = BenchmarkRunner().run(sizes=(10, 30), repeats=2)
        self.assertEqual(len(results), 3 * 4 * 2)
        for r in results:
            self.assertGreaterEqual(r.median_ns_per_op, 0)
            self.assertEqual(r.operations, r.dataset_size)
            self.assertEqual(r.repeat_count, 2)
        self.assertIn("Hash Table", format_results(results))
        self.assertIn("pengukuran", interpret(results))
        with tempfile.TemporaryDirectory() as d:
            path = export_csv(results, Path(d) / "benchmark.csv")
            self.assertTrue(path.exists())
            self.assertIn("median_ns_per_op", path.read_text(encoding="utf-8-sig"))

    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            BenchmarkRunner().run(repeats=0)
        with self.assertRaises(ValueError):
            BenchmarkRunner().run(sizes=(0,))
