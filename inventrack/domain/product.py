from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from inventrack.domain.exceptions import ValidationError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def money(value: object) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError("Harga harus berupa angka yang valid.") from exc
    if (not parsed.is_finite() or parsed < 0 or parsed > Decimal("999999999999.99")
            or parsed.as_tuple().exponent < -2):
        raise ValidationError("Harga harus 0–999.999.999.999,99 dengan maksimal 2 desimal.")
    try:
        return parsed.quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValidationError("Harga tidak dapat diproses.") from exc


def nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValidationError(f"{label} harus bilangan bulat tidak negatif.")
    return value


@dataclass(frozen=True, slots=True)
class Product:
    product_id: str
    name: str
    category: str
    brand: str
    price: Decimal
    stock: int = 0
    minimum_stock: int = 5
    description: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.product_id, str) or not self.product_id.strip():
            raise ValidationError("ID produk tidak boleh kosong.")
        if len(self.product_id) > 32 or any(c.isspace() for c in self.product_id):
            raise ValidationError("ID produk maksimal 32 karakter dan tanpa spasi.")
        for label, value in (("Nama", self.name), ("Kategori", self.category), ("Merek", self.brand)):
            if not isinstance(value, str) or not value.strip() or len(value) > 100:
                raise ValidationError(f"{label} wajib diisi dan maksimal 100 karakter.")
        if not isinstance(self.description, str) or len(self.description) > 500:
            raise ValidationError("Deskripsi maksimal 500 karakter.")
        object.__setattr__(self, "price", money(self.price))
        nonnegative_int(self.stock, "Stok")
        nonnegative_int(self.minimum_stock, "Stok minimum")
        if not self.created_at:
            object.__setattr__(self, "created_at", utc_now())
        if not self.updated_at:
            object.__setattr__(self, "updated_at", self.created_at)

    @property
    def inventory_value(self) -> Decimal:
        return self.price * self.stock

    @property
    def stock_status(self) -> str:
        if self.stock == 0:
            return "HABIS"
        if self.stock <= self.minimum_stock:
            return "RENDAH"
        return "AMAN"

    def change(self, **changes: object) -> "Product":
        return replace(self, **changes, updated_at=utc_now())

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id, "name": self.name,
            "category": self.category, "brand": self.brand,
            "price": str(self.price), "stock": self.stock,
            "minimum_stock": self.minimum_stock,
            "description": self.description,
            "created_at": self.created_at, "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        return cls(**data)
