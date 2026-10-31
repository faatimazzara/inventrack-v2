from dataclasses import dataclass
from pathlib import Path

from inventrack.auth.access_control import AccessControl
from inventrack.auth.auth_service import AuthService
from inventrack.repositories.hash_repository import HashRepository
from inventrack.services.audit_service import AuditService
from inventrack.services.product_service import ProductService
from inventrack.services.report_service import ReportService
from inventrack.services.search_service import SearchService
from inventrack.services.stock_service import StockService
from inventrack.storage.inventory_store import InventoryStore
from inventrack.storage.json_storage import JsonStorage
from inventrack.storage.user_store import UserStore


@dataclass
class AppContext:
    repository: HashRepository
    users: UserStore
    auth: AuthService
    access: AccessControl
    audit: AuditService
    products: ProductService
    stock: StockService
    search: SearchService
    reports: ReportService
    inventory_store: InventoryStore

    def save(self) -> None:
        self.inventory_store.save(self.repository, self.stock, self.audit)


def bootstrap(data_dir: Path | str) -> AppContext:
    root = Path(data_dir)
    users = UserStore(JsonStorage(root / "users.json"))
    access = AccessControl(users)
    auth = AuthService(users, access)
    repo = HashRepository()
    audit = AuditService(access)
    stock = StockService(repo, access, audit)
    inventory_store = InventoryStore(JsonStorage(root / "inventory.json"))
    context = AppContext(repo, users, auth, access, audit,
                         ProductService(repo, access, audit), stock,
                         SearchService(repo, access), ReportService(repo, access),
                         inventory_store)
    inventory_store.load(repo, stock, audit)
    return context
