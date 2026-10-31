from dataclasses import replace

from inventrack.domain.exceptions import AuthenticationError, ValidationError
from inventrack.domain.user import User
from inventrack.storage.json_storage import JsonStorage


class UserStore:
    def __init__(self, storage: JsonStorage) -> None:
        self._storage = storage
        raw = storage.read({"schema_version": 1, "users": []})
        if not isinstance(raw, dict) or raw.get("schema_version") != 1:
            raise ValidationError("Format berkas pengguna tidak didukung.")
        self._users = {record["username"].lower(): User.from_dict(record)
                       for record in raw.get("users", [])}

    def all(self) -> list[User]:
        return sorted(self._users.values(), key=lambda user: user.username)

    def get(self, username: str) -> User | None:
        return self._users.get(username.strip().lower())

    def put(self, user: User) -> None:
        key = user.username.lower()
        if key in self._users and self._users[key].username != user.username:
            raise ValidationError("Username dengan huruf berbeda sudah terpakai.")
        original = self._users.get(key)
        self._users[key] = user
        try:
            self._save()
        except Exception:
            if original is None:
                del self._users[key]
            else:
                self._users[key] = original
            raise

    def _save(self) -> None:
        self._storage.write({"schema_version": 1, "users":
                             [user.to_dict() for user in self.all()]})

    def count(self) -> int:
        return len(self._users)
