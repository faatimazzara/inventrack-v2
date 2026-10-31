from inventrack.domain.enums import Role, StockMovementType
from inventrack.domain.exceptions import (AuthorizationError, InsufficientStockError,
                                         ProductNotFoundError, ValidationError)
from tests.common import IntegrationCase


class StockServiceTests(IntegrationCase):
    def test_in_out_and_adjust(self):
        self.add_product()
        incoming = self.ctx.stock.move(self.admin, "PRD001", StockMovementType.IN, 20, "Restok")
        outgoing = self.ctx.stock.move(self.admin, "PRD001", StockMovementType.OUT, 7, "Penjualan")
        adjustment = self.ctx.stock.adjust(self.admin, "PRD001", 11, "Stock opname")
        self.assertEqual([incoming.after, outgoing.after, adjustment.after], [20, 13, 11])
        self.assertEqual(self.ctx.products.get(self.admin, "PRD001").stock, 11)
        self.assertEqual(len(self.ctx.stock.history(self.admin)), 3)

    def test_invalid_stock_does_not_mutate(self):
        self.add_product()
        with self.assertRaises(InsufficientStockError):
            self.ctx.stock.move(self.admin, "PRD001", StockMovementType.OUT, 1, "Jual")
        with self.assertRaises(ValidationError):
            self.ctx.stock.move(self.admin, "PRD001", StockMovementType.IN, 0, "Restok")
        with self.assertRaises(ValidationError):
            self.ctx.stock.adjust(self.admin, "PRD001", -1, "Salah")
        with self.assertRaises(ProductNotFoundError):
            self.ctx.stock.adjust(self.admin, "UNKNOWN", 1, "Salah")
        self.assertEqual(self.ctx.products.get(self.admin, "PRD001").stock, 0)
        self.assertEqual(self.ctx.stock.history(self.admin), [])

    def test_role_enforcement(self):
        self.add_product()
        staff = self.make_user(Role.STAFF)
        manager = self.make_user(Role.MANAGER, "manager01")
        self.ctx.stock.move(staff, "PRD001", StockMovementType.IN, 5, "Terima")
        with self.assertRaises(AuthorizationError):
            self.ctx.stock.adjust(staff, "PRD001", 10, "Opname")
        with self.assertRaises(AuthorizationError):
            self.ctx.stock.move(manager, "PRD001", StockMovementType.IN, 5, "Terima")
        self.assertEqual(len(self.ctx.stock.history(manager)), 1)

    def test_reports_and_audit(self):
        self.add_product()
        self.ctx.stock.move(self.admin, "PRD001", StockMovementType.IN, 8, "Restok")
        summary = self.ctx.reports.summary(self.admin)
        self.assertEqual(summary["total_products"], 1)
        self.assertEqual(summary["total_units"], 8)
        self.assertEqual(str(summary["total_value"]), "2000000.00")
        self.assertEqual(len(self.ctx.audit.list_events(self.admin)), 2)
