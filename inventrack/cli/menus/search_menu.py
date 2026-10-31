from inventrack.cli.input_helpers import show_product, show_products


def run(app) -> None:
    io, ctx, actor = app.io, app.ctx, app.user
    while True:
        choice = io.menu("PENCARIAN PRODUK", {
            "1": "Cari ID (Hash Table)", "2": "Cari berdasarkan nama",
            "3": "Filter kategori", "4": "Filter harga",
            "5": "Tampilkan seluruh produk", "6": "Filter stok rendah/habis"})
        if choice == "0":
            return
        if choice == "1":
            app.safe(lambda: show_product(io, ctx.products.get(actor, io.ask("ID produk: "))))
        elif choice == "2":
            app.safe(lambda: show_products(io, ctx.search.find(actor, name=io.ask("Cari nama: "))))
        elif choice == "3":
            app.safe(lambda: show_products(io, ctx.search.find(actor, category=io.ask("Kategori: "))))
        elif choice == "4":
            def action():
                lowest = io.decimal("Harga minimal: ")
                highest = io.decimal("Harga maksimal: ")
                show_products(io, ctx.search.find(actor, min_price=lowest, max_price=highest))
            app.safe(action)
        elif choice == "5":
            app.safe(lambda: show_products(io, ctx.products.list_all(actor)))
        elif choice == "6":
            def action():
                status = io.ask("Status (RENDAH/HABIS): ").upper()
                if status not in ("RENDAH", "HABIS"):
                    io.say("Status tidak valid.")
                    return
                show_products(io, ctx.search.find(actor, stock_status=status))
            app.safe(action)
        else:
            io.say("Pilihan menu tidak valid.")
