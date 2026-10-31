from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.domain.exceptions import StorageError
from inventrack.domain.product import Product
from inventrack.services.audit_service import AuditService
from inventrack.services.stock_service import StockService
from inventrack.storage.json_storage import JsonStorage


class InventoryStore:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def load(self, repo: InventoryRepository, stock: StockService,
             audit: AuditService) -> None:
        payload = self.storage.read({"schema_version": 1, "products": [],
                                     "transactions": [], "audit_events": []})
        if not isinstance(payload, dict) or payload.get("schema_version") != 1:
            raise StorageError("Format berkas inventaris tidak didukung.")
        try:
            for raw in payload.get("products", []):
                repo.insert(Product.from_dict(raw))
            stock.load(payload.get("transactions", []))
            audit.load(payload.get("audit_events", []))
        except (KeyError, ValueError, TypeError) as exc:
            raise StorageError(f"Data inventaris tidak valid: {exc}") from exc

    def save(self, repo: InventoryRepository, stock: StockService,
             audit: AuditService) -> None:
        self.storage.write({
            "schema_version": 1,
            "products": [product.to_dict() for product in repo.all()],
            "transactions": stock.all_for_storage(),
            "audit_events": audit.all_for_storage(),
        })
