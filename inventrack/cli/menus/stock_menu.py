from inventrack.domain.enums import Role, StockMovementType
from inventrack.cli.input_helpers import show_products


def run(app) -> None:
    io, ctx, actor = app.io, app.ctx, app.user
    while True:
        options = {"1": "Stok masuk", "2": "Stok keluar",
                   "3": "Stok rendah", "4": "Stok habis", "5": "Riwayat transaksi"}
        if actor.role == Role.ADMIN:
            options["6"] = "Penyesuaian stok (admin)"
        choice = io.menu("MANAJEMEN STOK", options)
        if choice == "0":
            return
        if choice in ("1", "2", "6") and (choice != "6" or actor.role == Role.ADMIN):
            def action():
                product_id = io.ask("ID produk: ")
                if choice == "6":
                    quantity = io.integer("Stok akhir yang benar: ")
                else:
                    quantity = io.integer("Jumlah: ", minimum=1)
                reason = io.ask("Alasan: ")
                tx = (ctx.stock.adjust(actor, product_id, quantity, reason) if choice == "6"
                      else ctx.stock.move(actor, product_id,
                                          StockMovementType.IN if choice == "1" else StockMovementType.OUT,
                                          quantity, reason))
                ctx.save()
                io.say(f"Berhasil. Stok {tx.product_id}: {tx.before} -> {tx.after} (ID: {tx.transaction_id[:8]}).")
            app.safe(action)
        elif choice in ("3", "4"):
            label = "RENDAH" if choice == "3" else "HABIS"
            app.safe(lambda: show_products(io, [p for p in ctx.products.list_all(actor)
                                                 if p.stock_status == label]))
        elif choice == "5":
            def action():
                product_id = io.ask("Filter ID produk (Enter=semua): ", required=False)
                transactions = ctx.stock.history(actor, product_id)
                if not transactions:
                    io.say("Belum ada transaksi.")
                for tx in transactions:
                    io.say(f"{tx.timestamp} | {tx.movement_type.value.upper():<6} | "
                           f"{tx.product_id} | {tx.before}->{tx.after} | "
                           f"{tx.actor} | {tx.reason}")
            app.safe(action)
        else:
            io.say("Pilihan menu tidak valid.")
