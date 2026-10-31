from dataclasses import dataclass

from inventrack.adt.inventory_repository import InventoryRepository
from inventrack.domain.exceptions import DuplicateProductError, ProductNotFoundError
from inventrack.domain.product import Product


@dataclass(slots=True)
class Node:
    value: Product
    next: "Node | None" = None


class LinkedRepository(InventoryRepository):
    """Custom singly linked list with tail pointer, without a dict index."""

    def __init__(self) -> None:
        self._head: Node | None = None
        self._tail: Node | None = None
        self._size = 0

    def insert(self, product: Product) -> None:
        if self.search(product.product_id) is not None:
            raise DuplicateProductError(f"ID {product.product_id} sudah terdaftar.")
        node = Node(product)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def search(self, product_id: str) -> Product | None:
        curr = self._head
        while curr is not None:
            if curr.value.product_id == product_id:
                return curr.value
            curr = curr.next
        return None

    def update(self, product: Product) -> None:
        curr = self._head
        while curr is not None:
            if curr.value.product_id == product.product_id:
                curr.value = product
                return
            curr = curr.next
        raise ProductNotFoundError(f"Produk {product.product_id} tidak ditemukan.")

    def delete(self, product_id: str) -> Product:
        prev: Node | None = None
        curr = self._head
        while curr is not None:
            if curr.value.product_id == product_id:
                if prev is None:
                    self._head = curr.next
                else:
                    prev.next = curr.next
                if curr is self._tail:
                    self._tail = prev
                self._size -= 1
                return curr.value
            prev, curr = curr, curr.next
        raise ProductNotFoundError(f"Produk {product_id} tidak ditemukan.")

    def all(self) -> list[Product]:
        results: list[Product] = []
        curr = self._head
        while curr is not None:
            results.append(curr.value)
            curr = curr.next
        return results

    def __len__(self) -> int:
        return self._size
