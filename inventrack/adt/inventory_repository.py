from abc import ABC, abstractmethod

from inventrack.domain.product import Product


class InventoryRepository(ABC):
    """ADT for unique-key inventory; every repository obeys identical semantics."""

    @abstractmethod
    def insert(self, product: Product) -> None:
        """Insert a product; raise DuplicateProductError if ID already exists."""

    @abstractmethod
    def search(self, product_id: str) -> Product | None:
        """Return matching product or None."""

    @abstractmethod
    def update(self, product: Product) -> None:
        """Replace an existing product; raise ProductNotFoundError otherwise."""

    @abstractmethod
    def delete(self, product_id: str) -> Product:
        """Delete and return product; raise ProductNotFoundError otherwise."""

    @abstractmethod
    def all(self) -> list[Product]:
        """Return products in insertion order."""

    @abstractmethod
    def __len__(self) -> int:
        """Return total products."""
