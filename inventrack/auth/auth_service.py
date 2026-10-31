from dataclasses import replace

from inventrack.auth.access_control import AccessControl
from inventrack.auth.password_hasher import PasswordHasher
from inventrack.domain.enums import Role
from inventrack.domain.exceptions import (AuthenticationError, AuthorizationError,
                                         ValidationError)
from inventrack.domain.user import User
from inventrack.storage.user_store import UserStore


class AuthService:
    def __init__(self, users: UserStore, access: AccessControl) -> None:
        self.users = users
        self.access = access

    def bootstrap_admin(self, username: str, full_name: str, password: str) -> User:
        if self.users.count():
            raise AuthorizationError("Admin awal hanya bisa dibuat saat database akun kosong.")
        user = User(username.strip(), full_name.strip(), Role.ADMIN,
                    PasswordHasher.hash_password(password))
        self.users.put(user)
        return user

    def login(self, username: str, password: str) -> User:
        user = self.users.get(username)
        if user is None or not user.active or not PasswordHasher.verify(password, user.password_hash):
            raise AuthenticationError("Username atau password salah, atau akun tidak aktif.")
        return user

    def add_user(self, actor: User, username: str, full_name: str,
                 password: str, role: Role) -> User:
        self.access.require(actor, Role.ADMIN)
        username = username.strip()
        if self.users.get(username) is not None:
            raise ValidationError("Username sudah digunakan.")
        user = User(username, full_name.strip(), role,
                    PasswordHasher.hash_password(password))
        self.users.put(user)
        return user

    def list_users(self, actor: User) -> list[User]:
        self.access.require(actor, Role.ADMIN)
        return self.users.all()

    def change_role(self, actor: User, username: str, new_role: Role) -> User:
        self.access.require(actor, Role.ADMIN)
        target = self._target(username)
        if target.username.lower() == actor.username.lower():
            raise ValidationError("Tidak bisa mengubah role akun sendiri.")
        self._protect_last_admin(target, new_role=new_role)
        updated = replace(target, role=new_role)
        self.users.put(updated)
        return updated

    def set_active(self, actor: User, username: str, active: bool) -> User:
        self.access.require(actor, Role.ADMIN)
        target = self._target(username)
        if target.username.lower() == actor.username.lower() and not active:
            raise ValidationError("Tidak bisa menonaktifkan akun sendiri.")
        self._protect_last_admin(target, active=active)
        updated = replace(target, active=active)
        self.users.put(updated)
        return updated

    def reset_password(self, actor: User, username: str, new_password: str) -> None:
        self.access.require(actor, Role.ADMIN)
        user = self._target(username)
        self.users.put(replace(user, password_hash=PasswordHasher.hash_password(new_password)))

    def change_own_password(self, actor: User, old_password: str,
                            new_password: str) -> None:
        current = self.access.require(actor, *tuple(Role))
        if not PasswordHasher.verify(old_password, current.password_hash):
            raise AuthenticationError("Password lama salah.")
        self.users.put(replace(current,
                               password_hash=PasswordHasher.hash_password(new_password)))

    def _target(self, username: str) -> User:
        user = self.users.get(username)
        if user is None:
            raise ValidationError("Akun tidak ditemukan.")
        return user

    def _protect_last_admin(self, user: User, *, new_role: Role | None = None,
                            active: bool | None = None) -> None:
        if user.role != Role.ADMIN or not user.active:
            return
        losing_admin = (new_role is not None and new_role != Role.ADMIN) or active is False
        if losing_admin and sum(u.active and u.role == Role.ADMIN
                                for u in self.users.all()) <= 1:
            raise ValidationError("Minimal harus ada satu admin aktif.")
