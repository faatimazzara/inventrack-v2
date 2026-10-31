from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.domain.exceptions import DuplicateProductError, ProductNotFoundError
from inventrack.domain.product import Product


class HashRepository(InventoryRepository):
    """Primary inventory using Python's built-in hash table (dict)."""

    def __init__(self) -> None:
        self._data: dict[str, Product] = {}

    def insert(self, product: Product) -> None:
        if product.product_id in self._data:
            raise DuplicateProductError(f"ID {product.product_id} sudah terdaftar.")
        self._data[product.product_id] = product

    def search(self, product_id: str) -> Product | None:
        return self._data.get(product_id)

    def update(self, product: Product) -> None:
        if product.product_id not in self._data:
            raise ProductNotFoundError(f"Produk {product.product_id} tidak ditemukan.")
        self._data[product.product_id] = product

    def delete(self, product_id: str) -> Product:
        try:
            return self._data.pop(product_id)
        except KeyError as exc:
            raise ProductNotFoundError(f"Produk {product_id} tidak ditemukan.") from exc

    def all(self) -> list[Product]:
        return list(self._data.values())

    def __len__(self) -> int:
        return len(self._data)
