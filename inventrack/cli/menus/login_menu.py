from inventrack.domain.enums import Role
from inventrack.cli.menus import (admin_menu, staff_menu,
                                  manager_menu, developer_menu)

ROLE_MENUS = {
    Role.ADMIN: admin_menu.run,
    Role.STAFF: staff_menu.run,
    Role.MANAGER: manager_menu.run,
    Role.DEVELOPER: developer_menu.run,
}


def first_admin(app) -> None:
    io = app.io
    while app.ctx.users.count() == 0:
        io.say("\nPENGATURAN PERTAMA — Buat akun Admin Inventaris")
        def action():
            username = io.ask("Username admin: ")
            full_name = io.ask("Nama lengkap: ")
            password = io.secret("Password (minimal 8 karakter): ")
            confirmation = io.secret("Ulangi password: ")
            if password != confirmation:
                io.say("Konfirmasi password tidak sama.")
                return
            app.ctx.auth.bootstrap_admin(username, full_name, password)
            io.say("Admin awal berhasil dibuat. Silakan login.")
        app.safe(action)


def run(app) -> None:
    io = app.io
    first_admin(app)
    while True:
        choice = io.menu("INVENTRACK v2.0 — HALAMAN LOGIN", {"1": "Login"}, back="Keluar Program")
        if choice == "0":
            io.say("Terima kasih telah menggunakan InvenTrack.")
            return
        if choice != "1":
            io.say("Pilihan menu tidak valid.")
            continue
        def login_action():
            username = io.ask("Username: ")
            password = io.secret("Password: ")
            user = app.ctx.auth.login(username, password)
            app.user = user
            io.say(f"Login berhasil: {user.full_name} ({user.role.value}).")
            try:
                ROLE_MENUS[user.role](app)
            finally:
                app.user = None
            io.say("Logout berhasil.")
        app.safe(login_action)
