from inventrack.cli.menus import analysis_menu, benchmark_menu, user_menu


def run(app) -> None:
    io = app.io
    routes = {"1": analysis_menu.run, "2": benchmark_menu.run,
              "3": user_menu.account_menu}
    while True:
        choice = io.menu(f"DEVELOPER / TIM IT | {app.user.username}", {
            "1": "Lab analisis struktur data", "2": "Benchmark performa",
            "3": "Pengaturan akun saya"}, back="Logout")
        if choice == "0":
            return
        if choice in routes:
            routes[choice](app)
        else:
            io.say("Pilihan menu tidak valid.")
