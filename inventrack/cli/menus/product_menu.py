from inventrack.cli.input_helpers import show_product, show_products
from inventrack.domain.product import Product


def run(app) -> None:
    io, ctx, actor = app.io, app.ctx, app.user
    while True:
        choice = io.menu("MANAJEMEN PRODUK (ADMIN)", {
            "1": "Tambah produk", "2": "Cari produk berdasarkan ID",
            "3": "Ubah informasi produk", "4": "Hapus produk",
            "5": "Tampilkan semua produk", "6": "Detail produk"})
        if choice == "0":
            return
        if choice == "1":
            def action():
                product = Product(product_id=io.ask("ID produk: "),
                                  name=io.ask("Nama: "), category=io.ask("Kategori: "),
                                  brand=io.ask("Merek: "), price=io.decimal("Harga: "),
                                  minimum_stock=io.integer("Stok minimum: "),
                                  description=io.ask("Deskripsi (boleh kosong): ", required=False))
                ctx.products.add(actor, product)
                ctx.save()
                io.say(f"Produk {product.product_id} berhasil ditambahkan. Stok awal: 0.")
            app.safe(action)
        elif choice in ("2", "6"):
            app.safe(lambda: show_product(io, ctx.products.get(actor, io.ask("ID produk: "))))
        elif choice == "3":
            def action():
                product_id = io.ask("ID yang akan diubah: ")
                show_product(io, ctx.products.get(actor, product_id))
                field = io.ask("Field (name/category/brand/price/minimum_stock/description): ")
                if field not in {"name", "category", "brand", "price", "minimum_stock", "description"}:
                    io.say("Field tidak dikenal.")
                    return
                if field == "price":
                    new_value = io.decimal("Nilai baru: ")
                elif field == "minimum_stock":
                    new_value = io.integer("Nilai baru: ")
                else:
                    new_value = io.ask("Nilai baru: ", required=field != "description")
                updated = ctx.products.update(actor, product_id, **{field: new_value})
                ctx.save()
                io.say("Produk berhasil diperbarui.")
                show_product(io, updated)
            app.safe(action)
        elif choice == "4":
            def action():
                product_id = io.ask("ID yang akan dihapus: ")
                show_product(io, ctx.products.get(actor, product_id))
                if io.yes("Hapus produk? (y/t): "):
                    ctx.products.delete(actor, product_id)
                    ctx.save()
                    io.say("Produk berhasil dihapus.")
                else:
                    io.say("Penghapusan dibatalkan.")
            app.safe(action)
        elif choice == "5":
            app.safe(lambda: show_products(io, ctx.products.list_all(actor)))
        else:
            io.say("Pilihan menu tidak valid.")
