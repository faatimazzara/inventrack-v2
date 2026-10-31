from inventrack.cli.menus import history_menu, report_menu, search_menu, user_menu


def run(app) -> None:
    io = app.io
    routes = {"1": report_menu.run, "2": search_menu.run,
              "3": history_menu.run, "4": user_menu.account_menu}
    while True:
        choice = io.menu(f"MANAJER INVENTARIS | {app.user.username}", {
            "1": "Laporan inventaris", "2": "Pencarian dan filter produk",
            "3": "Riwayat aktivitas", "4": "Pengaturan akun saya"}, back="Logout")
        if choice == "0":
            return
        if choice in routes:
            routes[choice](app)
        else:
            io.say("Pilihan menu tidak valid.")
