from decimal import Decimal

from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.auth.access_control import AccessControl
from inventrack.domain.enums import Role
from inventrack.domain.exceptions import ProductNotFoundError, ValidationError
from inventrack.domain.product import Product
from inventrack.domain.user import User
from inventrack.services.audit_service import AuditService


class ProductService:
    def __init__(self, repo: InventoryRepository, access: AccessControl,
                 audit: AuditService) -> None:
        self.repo, self.access, self.audit = repo, access, audit

    def add(self, actor: User, product: Product) -> Product:
        self.access.require(actor, Role.ADMIN)
        self.repo.insert(product)
        self.audit.record(actor, "PRODUCT_ADD", product.product_id)
        return product

    def get(self, actor: User, product_id: str) -> Product:
        self.access.require(actor, Role.ADMIN, Role.STAFF, Role.MANAGER)
        product = self.repo.search(product_id.strip())
        if product is None:
            raise ProductNotFoundError(f"Produk {product_id} tidak ditemukan.")
        return product

    def list_all(self, actor: User) -> list[Product]:
        self.access.require(actor, Role.ADMIN, Role.STAFF, Role.MANAGER)
        return self.repo.all()

    def update(self, actor: User, product_id: str, **changes: object) -> Product:
        self.access.require(actor, Role.ADMIN)
        forbidden = set(changes) - {"name", "category", "brand", "price",
                                     "minimum_stock", "description"}
        if forbidden:
            raise ValidationError(f"Atribut tidak bisa diubah: {', '.join(sorted(forbidden))}")
        old = self.get(actor, product_id)
        updated = old.change(**changes)
        self.repo.update(updated)
        self.audit.record(actor, "PRODUCT_UPDATE", product_id)
        return updated

    def delete(self, actor: User, product_id: str) -> Product:
        self.access.require(actor, Role.ADMIN)
        product = self.repo.delete(product_id.strip())
        self.audit.record(actor, "PRODUCT_DELETE", product.product_id)
        return product
