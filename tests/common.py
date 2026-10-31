import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from inventrack.bootstrap import bootstrap
from inventrack.domain.enums import Role
from inventrack.domain.product import Product


class IntegrationCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.path = Path(self.tempdir.name)
        self.ctx = bootstrap(self.path)
        self.admin = self.ctx.auth.bootstrap_admin("admin01", "Administrator", "Password123!")

    def add_product(self, product_id: str = "PRD001", stock: int = 0) -> Product:
        p = Product(product_id, "Keyboard", "Elektronik", "KeyCo",
                    Decimal("250000.00"), stock, 5)
        self.ctx.products.add(self.admin, p)
        return p

    def make_user(self, role: Role, username: str = "pengguna01"):
        return self.ctx.auth.add_user(self.admin, username, "Pengguna", "Password123!", role)
