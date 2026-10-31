import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal

from inventrack.domain.exceptions import ValidationError
from inventrack.domain.product import Product


class ProductTests(unittest.TestCase):
    def build(self, **changes):
        defaults = dict(product_id="P01", name="Mouse", category="Gadget",
                        brand="MBrand", price="90000", stock=4, minimum_stock=5)
        return Product(**{**defaults, **changes})

    def test_valid_product_and_low_stock(self):
        p = self.build()
        self.assertEqual(p.stock_status, "RENDAH")
        self.assertEqual(p.inventory_value, Decimal("360000.00"))

    def test_out_and_safe_stock(self):
        self.assertEqual(self.build(stock=0).stock_status, "HABIS")
        self.assertEqual(self.build(stock=6).stock_status, "AMAN")

    def test_validation_rejects_invalid_data(self):
        for change in ({"product_id": ""}, {"product_id": "HAS SPACE"},
                       {"name": " "}, {"price": -1}, {"price": "NaN"},
                       {"price": "0.123"}, {"stock": -1}, {"stock": 1.1},
                       {"minimum_stock": -1}):
            with self.subTest(change=change), self.assertRaises(ValidationError):
                self.build(**change)

    def test_change_does_not_mutate_original(self):
        original = self.build()
        updated = original.change(name="Mouse Baru")
        self.assertEqual(original.name, "Mouse")
        self.assertEqual(updated.name, "Mouse Baru")
        with self.assertRaises(FrozenInstanceError):
            original.name = "Edited"

    def test_serialization(self):
        original = self.build()
        self.assertEqual(Product.from_dict(original.to_dict()), original)
