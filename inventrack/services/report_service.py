from collections import Counter
from decimal import Decimal

from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.auth.access_control import AccessControl
from inventrack.domain.enums import Role
from inventrack.domain.user import User


class ReportService:
    def __init__(self, repo: InventoryRepository, access: AccessControl) -> None:
        self.repo, self.access = repo, access

    def summary(self, actor: User) -> dict:
        self.access.require(actor, Role.ADMIN, Role.MANAGER)
        products = self.repo.all()
        return {
            "total_products": len(products),
            "total_units": sum(p.stock for p in products),
            "total_value": sum((p.inventory_value for p in products), Decimal("0.00")),
            "low_stock": sum(p.stock_status == "RENDAH" for p in products),
            "out_of_stock": sum(p.stock == 0 for p in products),
            "categories": dict(sorted(Counter(p.category for p in products).items())),
        }

    def category_values(self, actor: User) -> dict[str, Decimal]:
        self.access.require(actor, Role.ADMIN, Role.MANAGER)
        results: dict[str, Decimal] = {}
        for product in self.repo.all():
            results[product.category] = results.get(product.category, Decimal("0.00")) + product.inventory_value
        return dict(sorted(results.items()))
