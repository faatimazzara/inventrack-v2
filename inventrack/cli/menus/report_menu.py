from inventrack.cli.input_helpers import show_products


def run(app) -> None:
    io, ctx, actor = app.io, app.ctx, app.user
    while True:
        choice = io.menu("LAPORAN INVENTARIS", {
            "1": "Ringkasan inventaris", "2": "Nilai persediaan per kategori",
            "3": "Produk stok rendah/habis", "4": "Peringkat stok tertinggi"})
        if choice == "0":
            return
        if choice == "1":
            def action():
                for key, value in ctx.reports.summary(actor).items():
                    io.say(f"{key:<21}: {value}")
            app.safe(action)
        elif choice == "2":
            def action():
                for category, value in ctx.reports.category_values(actor).items():
                    io.say(f"{category:<22}: Rp{value:,.2f}")
            app.safe(action)
        elif choice == "3":
            app.safe(lambda: show_products(io, [p for p in ctx.products.list_all(actor)
                                                 if p.stock_status in ("RENDAH", "HABIS")]))
        elif choice == "4":
            app.safe(lambda: show_products(io, sorted(ctx.products.list_all(actor),
                                                       key=lambda p: p.stock, reverse=True)[:20]))
        else:
            io.say("Pilihan menu tidak valid.")
