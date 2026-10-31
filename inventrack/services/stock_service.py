from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.auth.access_control import AccessControl
from inventrack.domain.enums import Role, StockMovementType
from inventrack.domain.exceptions import (InsufficientStockError, ProductNotFoundError,
                                         ValidationError)
from inventrack.domain.product import nonnegative_int
from inventrack.domain.stock_transaction import StockTransaction
from inventrack.domain.user import User
from inventrack.services.audit_service import AuditService


class StockService:
    def __init__(self, repo: InventoryRepository, access: AccessControl,
                 audit: AuditService) -> None:
        self.repo, self.access, self.audit = repo, access, audit
        self._transactions: list[StockTransaction] = []

    def move(self, actor: User, product_id: str, movement_type: StockMovementType,
             quantity: int, reason: str) -> StockTransaction:
        self.access.require(actor, Role.ADMIN, Role.STAFF)
        if movement_type not in (StockMovementType.IN, StockMovementType.OUT):
            raise ValidationError("Jenis transaksi harus stok masuk atau keluar.")
        nonnegative_int(quantity, "Jumlah")
        if quantity == 0:
            raise ValidationError("Jumlah transaksi harus lebih dari nol.")
        return self._apply(actor, product_id, movement_type, quantity, reason)

    def adjust(self, actor: User, product_id: str, new_stock: int,
               reason: str) -> StockTransaction:
        self.access.require(actor, Role.ADMIN)
        nonnegative_int(new_stock, "Stok baru")
        return self._apply(actor, product_id, StockMovementType.ADJUST, new_stock, reason)

    def _apply(self, actor: User, product_id: str,
               movement_type: StockMovementType, quantity: int,
               reason: str) -> StockTransaction:
        if not isinstance(reason, str) or not reason.strip():
            raise ValidationError("Alasan transaksi wajib diisi.")
        product = self.repo.search(product_id.strip())
        if product is None:
            raise ProductNotFoundError(f"Produk {product_id} tidak ditemukan.")
        before = product.stock
        after = (before + quantity if movement_type == StockMovementType.IN
                 else before - quantity if movement_type == StockMovementType.OUT
                 else quantity)
        if after < 0:
            raise InsufficientStockError(f"Stok tersedia hanya {before} unit.")
        transaction = StockTransaction.create(product.product_id, movement_type,
                                              before, after, reason.strip(), actor.username)
        self.repo.update(product.change(stock=after))
        self._transactions.append(transaction)
        self.audit.record(actor, f"STOCK_{movement_type.value.upper()}",
                          f"{product.product_id}: {before} -> {after}")
        return transaction

    def history(self, actor: User, product_id: str = "", limit: int = 100) -> list[StockTransaction]:
        self.access.require(actor, Role.ADMIN, Role.STAFF, Role.MANAGER)
        matching = (tx for tx in self._transactions
                    if not product_id or tx.product_id == product_id.strip())
        return list(reversed(list(matching)[-limit:]))

    def all_for_storage(self) -> list[dict]:
        return [tx.to_dict() for tx in self._transactions]

    def load(self, data: list[dict]) -> None:
        self._transactions = [StockTransaction.from_dict(item) for item in data]
