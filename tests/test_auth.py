from inventrack.auth.password_hasher import PasswordHasher
from inventrack.domain.enums import Role
from inventrack.domain.exceptions import (AuthenticationError, AuthorizationError,
                                         ValidationError)
from tests.common import IntegrationCase


class AuthTests(IntegrationCase):
    def test_password_hash_and_login(self):
        saved = self.ctx.users.get("admin01")
        self.assertNotIn("Password123!", saved.password_hash)
        self.assertTrue(PasswordHasher.verify("Password123!", saved.password_hash))
        self.assertFalse(PasswordHasher.verify("wrong", saved.password_hash))
        self.assertEqual(self.ctx.auth.login("admin01", "Password123!").role, Role.ADMIN)
        with self.assertRaises(AuthenticationError):
            self.ctx.auth.login("admin01", "bad")

    def test_admin_can_create_all_roles(self):
        for i, role in enumerate(Role):
            user = self.make_user(role, f"user{i:02d}")
            self.assertEqual(self.ctx.auth.login(user.username, "Password123!").role, role)
        self.assertEqual(len(self.ctx.auth.list_users(self.admin)), 5)

    def test_staff_cannot_manage_accounts(self):
        staff = self.make_user(Role.STAFF)
        with self.assertRaises(AuthorizationError):
            self.ctx.auth.list_users(staff)
        with self.assertRaises(AuthorizationError):
            self.ctx.auth.add_user(staff, "baduser", "Bad", "Password123!", Role.ADMIN)

    def test_disabled_account_cannot_login(self):
        staff = self.make_user(Role.STAFF)
        self.ctx.auth.set_active(self.admin, staff.username, False)
        with self.assertRaises(AuthenticationError):
            self.ctx.auth.login(staff.username, "Password123!")
        with self.assertRaises(AuthenticationError):
            self.ctx.access.require(staff, Role.STAFF)

    def test_change_role_revokes_old_privileges(self):
        staff = self.make_user(Role.STAFF)
        self.ctx.auth.change_role(self.admin, staff.username, Role.MANAGER)
        with self.assertRaises(AuthorizationError):
            self.ctx.access.require(staff, Role.STAFF)
        self.assertEqual(self.ctx.access.require(staff, Role.MANAGER).role, Role.MANAGER)

    def test_password_reset_and_self_change(self):
        staff = self.make_user(Role.STAFF)
        self.ctx.auth.reset_password(self.admin, staff.username, "Changed123!")
        with self.assertRaises(AuthenticationError):
            self.ctx.auth.login(staff.username, "Password123!")
        self.ctx.auth.change_own_password(staff, "Changed123!", "Updated123!")
        self.assertEqual(self.ctx.auth.login(staff.username, "Updated123!").username, staff.username)

    def test_cannot_disable_last_admin(self):
        with self.assertRaises(ValidationError):
            self.ctx.auth.set_active(self.admin, "admin01", False)
        second_admin = self.make_user(Role.ADMIN)
        self.ctx.auth.set_active(self.admin, second_admin.username, False)
        self.assertTrue(self.ctx.users.get("admin01").active)

    def test_password_policy(self):
        with self.assertRaises(ValidationError):
            PasswordHasher.hash_password("short")

    def test_unauthorized_bootstrap(self):
        with self.assertRaises(AuthorizationError):
            self.ctx.auth.bootstrap_admin("newadmin", "New Admin", "Password123!")
