from inventrack.cli.menus import (history_menu, product_menu, report_menu,
                                   search_menu, stock_menu, user_menu)


def run(app) -> None:
    io = app.io
    routes = {"1": product_menu.run, "2": stock_menu.run,
              "3": search_menu.run, "4": report_menu.run,
              "5": history_menu.run, "6": user_menu.run,
              "7": user_menu.account_menu}
    while True:
        choice = io.menu(f"ADMIN INVENTARIS | {app.user.username}", {
            "1": "Manajemen produk", "2": "Manajemen stok",
            "3": "Pencarian produk", "4": "Laporan inventaris",
            "5": "Riwayat aktivitas", "6": "Manajemen akun pengguna",
            "7": "Pengaturan akun saya"}, back="Logout")
        if choice == "0":
            return
        if choice in routes:
            routes[choice](app)
        else:
            io.say("Pilihan menu tidak valid.")
