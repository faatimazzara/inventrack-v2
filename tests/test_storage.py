from decimal import Decimal

from inventrack.bootstrap import bootstrap
from inventrack.domain.enums import Role, StockMovementType
from inventrack.domain.exceptions import StorageError
from inventrack.storage.json_storage import JsonStorage
from tests.common import IntegrationCase


class PersistenceTests(IntegrationCase):
    def test_reload_all_data(self):
        self.add_product()
        self.ctx.stock.move(self.admin, "PRD001", StockMovementType.IN, 3, "Restok")
        staff = self.make_user(Role.STAFF)
        self.ctx.save()
        new = bootstrap(self.path)
        admin = new.auth.login("admin01", "Password123!")
        self.assertEqual(new.products.get(admin, "PRD001").stock, 3)
        self.assertEqual(len(new.stock.history(admin)), 1)
        self.assertEqual(len(new.audit.list_events(admin)), 2)
        self.assertEqual(new.auth.login(staff.username, "Password123!").role, Role.STAFF)

    def test_read_corrupted_json_does_not_silently_overwrite(self):
        file = self.path / "inventory.json"
        file.write_text("{not valid json", encoding="utf-8")
        with self.assertRaises(StorageError):
            bootstrap(self.path)
        self.assertEqual(file.read_text(encoding="utf-8"), "{not valid json")

    def test_bad_schema(self):
        JsonStorage(self.path / "inventory.json").write({"schema_version": 999})
        with self.assertRaises(StorageError):
            bootstrap(self.path)
