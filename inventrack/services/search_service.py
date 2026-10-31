from decimal import Decimal

from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.auth.access_control import AccessControl
from inventrack.domain.enums import Role
from inventrack.domain.product import Product, money
from inventrack.domain.user import User


class SearchService:
    def __init__(self, repo: InventoryRepository, access: AccessControl) -> None:
        self.repo, self.access = repo, access

    def find(self, actor: User, *, name: str = "", category: str = "",
             min_price: Decimal | None = None, max_price: Decimal | None = None,
             stock_status: str = "") -> list[Product]:
        self.access.require(actor, Role.ADMIN, Role.STAFF, Role.MANAGER)
        minimum = money(min_price) if min_price is not None else None
        maximum = money(max_price) if max_price is not None else None
        products = self.repo.all()
        return [p for p in products
                if (not name or name.casefold() in p.name.casefold())
                and (not category or category.casefold() in p.category.casefold())
                and (minimum is None or p.price >= minimum)
                and (maximum is None or p.price <= maximum)
                and (not stock_status or p.stock_status == stock_status.upper())]
