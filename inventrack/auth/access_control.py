from inventrack.domain.enums import Role
from inventrack.domain.exceptions import AuthenticationError, AuthorizationError
from inventrack.domain.user import User
from inventrack.storage.user_store import UserStore


class AccessControl:
    def __init__(self, users: UserStore) -> None:
        self.users = users

    def require(self, actor: User, *roles: Role) -> User:
        current = self.users.get(actor.username)
        if current is None or not current.active:
            raise AuthenticationError("Sesi tidak berlaku. Silakan login kembali.")
        if current.role not in roles:
            raise AuthorizationError("Akses ditolak untuk role ini.")
        return current
