from inventrack.domain.enums import Role
from inventrack.domain.exceptions import ValidationError


def account_menu(app) -> None:
    io, ctx, actor = app.io, app.ctx, app.user
    while True:
        choice = io.menu("PENGATURAN AKUN SAYA", {"1": "Ganti password"})
        if choice == "0":
            return
        if choice == "1":
            def action():
                old = io.secret("Password lama: ")
                new = io.secret("Password baru: ")
                ctx.auth.change_own_password(actor, old, new)
                io.say("Password berhasil diubah.")
            app.safe(action)
        else:
            io.say("Pilihan menu tidak valid.")


def run(app) -> None:
    io, ctx, actor = app.io, app.ctx, app.user
    while True:
        choice = io.menu("MANAJEMEN PENGGUNA (ADMIN)", {
            "1": "Tambah akun", "2": "Daftar akun", "3": "Ubah role pengguna",
            "4": "Aktifkan/nonaktifkan akun", "5": "Reset password pengguna"})
        if choice == "0":
            return
        if choice == "1":
            def action():
                username = io.ask("Username: ")
                full_name = io.ask("Nama lengkap: ")
                role = Role(io.ask("Role (admin/staff/manager/developer): ").lower())
                pwd = io.secret("Password baru (min. 8 karakter): ")
                user = ctx.auth.add_user(actor, username, full_name, pwd, role)
                ctx.audit.record(actor, "USER_ADD", user.username)
                ctx.save()
                io.say(f"Akun {user.username} dibuat sebagai {user.role.value}.")
            app.safe(action)
        elif choice == "2":
            def action():
                for user in ctx.auth.list_users(actor):
                    io.say(f"{user.username:<15} {user.role.value:<11} "
                           f"{'AKTIF' if user.active else 'NONAKTIF':<9} {user.full_name}")
            app.safe(action)
        elif choice == "3":
            def action():
                username = io.ask("Username: ")
                role = Role(io.ask("Role baru (admin/staff/manager/developer): ").lower())
                ctx.auth.change_role(actor, username, role)
                ctx.audit.record(actor, "USER_ROLE", f"{username}: {role.value}")
                ctx.save()
                io.say("Role berhasil diperbarui.")
            app.safe(action)
        elif choice == "4":
            def action():
                username = io.ask("Username: ")
                active = io.ask("Aktif? (y/t): ").lower() == "y"
                ctx.auth.set_active(actor, username, active)
                ctx.audit.record(actor, "USER_STATUS", f"{username}: {active}")
                ctx.save()
                io.say("Status akun diperbarui.")
            app.safe(action)
        elif choice == "5":
            def action():
                username = io.ask("Username: ")
                pwd = io.secret("Password baru: ")
                ctx.auth.reset_password(actor, username, pwd)
                ctx.audit.record(actor, "USER_PASSWORD_RESET", username)
                ctx.save()
                io.say("Password pengguna direset.")
            app.safe(action)
        else:
            io.say("Pilihan menu tidak valid.")
