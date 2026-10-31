from decimal import Decimal

from inventrack.domain.enums import Role
from inventrack.domain.exceptions import (AuthorizationError, DuplicateProductError,
                                         ProductNotFoundError, ValidationError)
from tests.common import IntegrationCase


class ProductServiceTests(IntegrationCase):
    def test_add_search_update_delete(self):
        p = self.add_product()
        self.assertEqual(self.ctx.products.get(self.admin, "PRD001"), p)
        with self.assertRaises(DuplicateProductError):
            self.ctx.products.add(self.admin, p)
        updated = self.ctx.products.update(self.admin, "PRD001", price=300000)
        self.assertEqual(updated.price, Decimal("300000.00"))
        self.assertEqual(updated.stock, p.stock)
        self.assertEqual(self.ctx.products.delete(self.admin, "PRD001").product_id, "PRD001")
        with self.assertRaises(ProductNotFoundError):
            self.ctx.products.get(self.admin, "PRD001")

    def test_disallow_update_stock_through_product_service(self):
        self.add_product()
        with self.assertRaises(ValidationError):
            self.ctx.products.update(self.admin, "PRD001", stock=999)

    def test_roles(self):
        self.add_product()
        staff = self.make_user(Role.STAFF)
        manager = self.make_user(Role.MANAGER, "manager01")
        developer = self.make_user(Role.DEVELOPER, "developer01")
        self.assertEqual(self.ctx.products.get(staff, "PRD001").product_id, "PRD001")
        self.assertEqual(len(self.ctx.products.list_all(manager)), 1)
        for user in (staff, manager, developer):
            with self.assertRaises(AuthorizationError):
                self.ctx.products.delete(user, "PRD001")
        with self.assertRaises(AuthorizationError):
            self.ctx.products.get(developer, "PRD001")

    def test_search_filters(self):
        self.add_product()
        self.assertEqual(len(self.ctx.search.find(self.admin, name="key")), 1)
        self.assertEqual(len(self.ctx.search.find(self.admin, category="elektro")), 1)
        self.assertEqual(len(self.ctx.search.find(self.admin, min_price=300000)), 0)
        self.assertEqual(len(self.ctx.search.find(self.admin, stock_status="HABIS")), 1)

    def test_audit_products(self):
        self.add_product()
        self.ctx.products.update(self.admin, "PRD001", name="Baru")
        self.ctx.products.delete(self.admin, "PRD001")
        actions = [event.action for event in self.ctx.audit.list_events(self.admin)]
        self.assertEqual(actions, ["PRODUCT_DELETE", "PRODUCT_UPDATE", "PRODUCT_ADD"])
