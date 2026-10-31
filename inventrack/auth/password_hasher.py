import hashlib
import hmac
import secrets

from inventrack.domain.exceptions import ValidationError


class PasswordHasher:
    ITERATIONS = 310_000

    @staticmethod
    def _valid_password(password: str) -> None:
        if not isinstance(password, str) or len(password) < 8 or len(password) > 128:
            raise ValidationError("Password harus memiliki 8–128 karakter.")

    @classmethod
    def hash_password(cls, password: str) -> str:
        cls._valid_password(password)
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                     salt, cls.ITERATIONS)
        return f"pbkdf2_sha256${cls.ITERATIONS}${salt.hex()}${digest.hex()}"

    @staticmethod
    def verify(password: str, encoded: str) -> bool:
        try:
            algorithm, rounds, salt, digest = encoded.split("$")
            if algorithm != "pbkdf2_sha256":
                return False
            count = int(rounds)
            if not 100_000 <= count <= 1_000_000:
                return False
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                         bytes.fromhex(salt), count)
            return hmac.compare_digest(actual, bytes.fromhex(digest))
        except (TypeError, ValueError, AttributeError):
            return False
