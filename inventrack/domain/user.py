from dataclasses import dataclass

from inventrack.domain.enums import Role
from inventrack.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class User:
    username: str
    full_name: str
    role: Role
    password_hash: str
    active: bool = True

    def __post_init__(self) -> None:
        if (not isinstance(self.username, str) or not 3 <= len(self.username) <= 32
                or not self.username.replace("_", "").isalnum()):
            raise ValidationError("Username harus 3–32 karakter huruf, angka, atau underscore.")
        if not isinstance(self.full_name, str) or not self.full_name.strip():
            raise ValidationError("Nama lengkap wajib diisi.")
        if not isinstance(self.role, Role):
            raise ValidationError("Role pengguna tidak valid.")
        if not isinstance(self.password_hash, str) or not self.password_hash:
            raise ValidationError("Hash password tidak valid.")

    def public_dict(self) -> dict:
        return {"username": self.username, "full_name": self.full_name,
                "role": self.role.value, "active": self.active}

    def to_dict(self) -> dict:
        return {**self.public_dict(), "password_hash": self.password_hash}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(username=data["username"], full_name=data["full_name"],
                   role=Role(data["role"]), password_hash=data["password_hash"],
                   active=data.get("active", True))
