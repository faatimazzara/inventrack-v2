from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.domain.exceptions import DuplicateProductError, ProductNotFoundError
from inventrack.domain.product import Product


class ArrayRepository(InventoryRepository):
    """Dynamic array via Python list; searches by product ID are linear."""

    def __init__(self) -> None:
        self._items: list[Product] = []

    def insert(self, product: Product) -> None:
        if self.search(product.product_id) is not None:
            raise DuplicateProductError(f"ID {product.product_id} sudah terdaftar.")
        self._items.append(product)

    def search(self, product_id: str) -> Product | None:
        for item in self._items:
            if item.product_id == product_id:
                return item
        return None

    def update(self, product: Product) -> None:
        for i, item in enumerate(self._items):
            if item.product_id == product.product_id:
                self._items[i] = product
                return
        raise ProductNotFoundError(f"Produk {product.product_id} tidak ditemukan.")

    def delete(self, product_id: str) -> Product:
        for i, item in enumerate(self._items):
            if item.product_id == product_id:
                return self._items.pop(i)
        raise ProductNotFoundError(f"Produk {product_id} tidak ditemukan.")

    def all(self) -> list[Product]:
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)
