from inventrack.cli.menus import search_menu, stock_menu, user_menu


def run(app) -> None:
    io = app.io
    routes = {"1": search_menu.run, "2": stock_menu.run,
              "3": user_menu.account_menu}
    while True:
        choice = io.menu(f"STAF GUDANG | {app.user.username}", {
            "1": "Lihat/cari produk", "2": "Transaksi stok dan riwayat",
            "3": "Pengaturan akun saya"}, back="Logout")
        if choice == "0":
            return
        if choice in routes:
            routes[choice](app)
        else:
            io.say("Pilihan menu tidak valid.")
