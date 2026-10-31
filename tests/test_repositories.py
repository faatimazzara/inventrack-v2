import unittest
from decimal import Decimal

from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.domain.exceptions import DuplicateProductError, ProductNotFoundError
from inventrack.domain.product import Product
from inventrack.repositories.array_repository import ArrayRepository
from inventrack.repositories.linked_repository import LinkedRepository
from inventrack.repositories.hash_repository import HashRepository


class RepositoryContractTests(unittest.TestCase):
    def test_each_implementation(self):
        for repo_type in (ArrayRepository, LinkedRepository, HashRepository):
            with self.subTest(repository=repo_type.__name__):
                repo = repo_type()
                self.assertIsInstance(repo, InventoryRepository)
                self.assertEqual(len(repo), 0)
                records = [Product(f"P{i}", f"Item{i}", "Elektronik", "X", Decimal("100"))
                           for i in range(4)]
                for p in records:
                    repo.insert(p)
                self.assertEqual(len(repo), 4)
                self.assertEqual(repo.all(), records)
                self.assertIsNone(repo.search("UNKNOWN"))
                with self.assertRaises(DuplicateProductError):
                    repo.insert(records[0])
                updated = records[2].change(name="Baru")
                repo.update(updated)
                self.assertEqual(repo.search("P2"), updated)
                self.assertEqual(repo.delete("P0"), records[0])
                self.assertEqual(repo.delete("P3"), records[3])
                self.assertEqual(repo.delete("P1"), records[1])
                self.assertEqual(repo.delete("P2"), updated)
                self.assertEqual(len(repo), 0)
                self.assertEqual(repo.all(), [])
                with self.assertRaises(ProductNotFoundError):
                    repo.delete("P2")
                with self.assertRaises(ProductNotFoundError):
                    repo.update(records[0])

    def test_linked_list_head_tail_invariants(self):
        repo = LinkedRepository()
        a = Product("A", "A", "cat", "brand", 10)
        b = Product("B", "B", "cat", "brand", 10)
        c = Product("C", "C", "cat", "brand", 10)
        repo.insert(a)
        repo.delete("A")
        self.assertEqual(len(repo), 0)
        repo.insert(b)
        repo.insert(c)
        repo.delete("C")
        repo.insert(a)
        self.assertEqual([p.product_id for p in repo.all()], ["B", "A"])
        repo.delete("B")
        repo.delete("A")
        self.assertEqual(len(repo), 0)

    def test_large_consistency_without_dict_index_on_linked(self):
        arrays = [ArrayRepository(), LinkedRepository(), HashRepository()]
        products = [Product(f"S{i}", "Item", "cat", "brand", 10) for i in range(120)]
        for repo in arrays:
            for product in products:
                repo.insert(product)
            for i in range(0, 120, 3):
                repo.delete(f"S{i}")
        self.assertEqual(arrays[0].all(), arrays[1].all())
        self.assertEqual(arrays[1].all(), arrays[2].all())
