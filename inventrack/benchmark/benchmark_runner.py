from dataclasses import dataclass
from statistics import mean, median
from time import perf_counter_ns
from typing import Callable

from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.benchmark.data_generator import make_products
from inventrack.repositories.array_repository import ArrayRepository
from inventrack.repositories.hash_repository import HashRepository
from inventrack.repositories.linked_repository import LinkedRepository

REPOSITORIES: dict[str, type[InventoryRepository]] = {
    "Array-based List": ArrayRepository,
    "Singly Linked List": LinkedRepository,
    "Hash Table (dict)": HashRepository,
}
OPERATIONS = ("insert", "search_hit", "search_miss", "delete")


@dataclass(frozen=True)
class BenchmarkResult:
    repository: str
    operation: str
    dataset_size: int
    operations: int
    repeat_count: int
    mean_ns_per_op: float
    median_ns_per_op: float
    min_ns_per_op: float
    max_ns_per_op: float

    def to_dict(self) -> dict:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


class BenchmarkRunner:
    """Fair, identical workloads; setup and data generation are not timed."""

    def run(self, sizes: tuple[int, ...] = (100, 500, 1000),
            repeats: int = 3, operations: tuple[str, ...] = OPERATIONS) -> list[BenchmarkResult]:
        if not 1 <= repeats <= 20:
            raise ValueError("Pengulangan harus 1 sampai 20.")
        if not operations or any(op not in OPERATIONS for op in operations):
            raise ValueError("Operasi benchmark tidak valid.")
        results = []
        for size in sizes:
            products = make_products(size)
            hit_ids = [p.product_id for p in products]
            miss_ids = [f"MISS-{i:08d}" for i in range(size)]
            for name, factory in REPOSITORIES.items():
                for operation in operations:
                    samples = []
                    for _ in range(repeats):
                        repo = factory()
                        if operation != "insert":
                            for product in products:
                                repo.insert(product)
                        start = perf_counter_ns()
                        if operation == "insert":
                            for product in products:
                                repo.insert(product)
                        elif operation == "search_hit":
                            for product_id in hit_ids:
                                if repo.search(product_id) is None:
                                    raise AssertionError("Benchmark gagal: data seharusnya ditemukan")
                        elif operation == "search_miss":
                            for product_id in miss_ids:
                                if repo.search(product_id) is not None:
                                    raise AssertionError("Benchmark gagal: data seharusnya tidak ditemukan")
                        elif operation == "delete":
                            for product_id in hit_ids:
                                repo.delete(product_id)
                        elapsed = perf_counter_ns() - start
                        samples.append(elapsed / size)
                        if operation == "insert" and len(repo) != size:
                            raise AssertionError("Jumlah produk hasil insert tidak sesuai")
                        if operation == "delete" and len(repo) != 0:
                            raise AssertionError("Produk hasil delete belum kosong")
                    results.append(BenchmarkResult(name, operation, size, size, repeats,
                                                   mean(samples), median(samples),
                                                   min(samples), max(samples)))
        return results
