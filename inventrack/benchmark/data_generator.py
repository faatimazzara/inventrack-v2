from decimal import Decimal

from inventrack.domain.product import Product


def make_products(count: int) -> list[Product]:
    if not 1 <= count <= 100_000:
        raise ValueError("Jumlah data benchmark harus 1 sampai 100.000.")
    return [Product(product_id=f"PRD{i:08d}", name=f"Produk {i}",
                    category=f"Kategori{i % 7}", brand="Benchmark",
                    price=Decimal("10000.00"), stock=10)
            for i in range(count)]
