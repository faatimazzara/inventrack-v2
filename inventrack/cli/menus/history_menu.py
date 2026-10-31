def run(app) -> None:
    io, ctx, actor = app.io, app.ctx, app.user
    while True:
        choice = io.menu("RIWAYAT AKTIVITAS", {"1": "Semua aktivitas terbaru",
                                                "2": "Cari aktivitas berdasarkan jenis"})
        if choice == "0":
            return
        if choice in ("1", "2"):
            def action():
                action_filter = io.ask("Cari aksi (mis. PRODUCT_ADD): ") if choice == "2" else ""
                events = ctx.audit.list_events(actor)
                filtered = [e for e in events if action_filter.upper() in e.action]
                if not filtered:
                    io.say("Belum ada aktivitas.")
                for e in filtered:
                    io.say(f"{e.timestamp} | {e.actor:<12} | {e.action:<15} | {e.details}")
            app.safe(action)
        else:
            io.say("Pilihan menu tidak valid.")
