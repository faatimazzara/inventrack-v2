from inventrack.cli.app import App
from inventrack.cli.input_helpers import TerminalIO
from inventrack.domain.enums import Role
from tests.common import IntegrationCase


class CLITests(IntegrationCase):
    def drive(self, choices: list[str], password: str = "Password123!") -> str:
        inputs = iter(choices)
        output: list[str] = []
        io = TerminalIO(read=lambda _: next(inputs), password=lambda _: password,
                        write=lambda value: output.append(value))
        App(self.ctx, io=io, output_dir=self.path / "outputs").run()
        return "\n".join(output)

    def test_admin_can_add_product_then_logout(self):
        result = self.drive(["1", "admin01", "1", "1", "P001", "Monitor",
                             "Perangkat", "Brand", "1500000", "3", "Layar",
                             "0", "0", "0"])
        self.assertIn("Produk P001 berhasil", result)
        self.assertIn("Logout berhasil", result)
        self.assertIn("Keluar Program", result)
        self.assertEqual(self.ctx.repository.search("P001").name, "Monitor")

    def test_staff_has_no_benchmark_menu(self):
        self.make_user(Role.STAFF, "staff01")
        result = self.drive(["1", "staff01", "0", "0"])
        self.assertIn("STAF GUDANG", result)
        self.assertNotIn("BENCHMARK STRUKTUR DATA", result)

    def test_manager_report_flow(self):
        self.make_user(Role.MANAGER, "manager01")
        result = self.drive(["1", "manager01", "1", "1", "0", "0", "0"])
        self.assertIn("total_products", result)
        self.assertNotIn("Manajemen akun pengguna", result)

    def test_developer_analysis_flow(self):
        self.make_user(Role.DEVELOPER, "developer01")
        result = self.drive(["1", "developer01", "1", "2", "0", "0", "0"])
        self.assertIn("O(1) rata-rata", result)
        self.assertIn("Benchmark performa", result)
        self.assertNotIn("Manajemen stok", result)

    def test_invalid_menu_and_back(self):
        result = self.drive(["wrong", "1", "admin01", "wrong", "0", "0"])
        self.assertIn("Pilihan menu tidak valid", result)

    def test_login_rejected(self):
        result = self.drive(["1", "wronguser", "0"])
        self.assertIn("[GAGAL]", result)

    def test_blank_menu_input_recovers(self):
        result = self.drive(["", "0"])
        self.assertIn("Pilihan menu tidak valid", result)

    def test_admin_stock_flow_and_persistence(self):
        self.add_product()
        result = self.drive(["1", "admin01", "2", "1", "PRD001", "10", "Restok",
                             "2", "PRD001", "3", "Penjualan",
                             "5", "", "0", "0", "0"])
        self.assertIn("PRD001: 0 -> 10", result)
        self.assertIn("PRD001: 10 -> 7", result)
        self.assertIn("Penjualan", result)
        self.assertEqual(self.ctx.repository.search("PRD001").stock, 7)

    def test_admin_user_add_and_subsequent_login(self):
        # Same known password is used for all prompts in this IO simulation.
        result = self.drive(["1", "admin01", "6", "1", "staff02", "Staff Test", "staff",
                             "0", "0", "1", "staff02", "0", "0"])
        self.assertIn("Akun staff02 dibuat", result)
        self.assertIn("STAF GUDANG | staff02", result)

    def test_developer_real_benchmark_csv(self):
        self.make_user(Role.DEVELOPER, "devbench")
        result = self.drive(["1", "devbench", "2", "5", "10", "1",
                             "7", "8", "0", "0", "0"])
        self.assertIn("Hash Table (dict)", result)
        self.assertIn("Analisis berdasarkan MEDIAN", result)
        self.assertTrue((self.path / "outputs" / "benchmark.csv").exists())

    def test_first_run_admin_creation(self):
        from inventrack.bootstrap import bootstrap
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            ctx = bootstrap(d)
            inputs = iter(["firstadmin", "Admin Pertama", "1", "firstadmin", "0", "0"])
            output = []
            io = TerminalIO(read=lambda _: next(inputs),
                            password=lambda _: "Password123!",
                            write=output.append)
            App(ctx, io=io).run()
            self.assertIn("Admin awal berhasil dibuat", "\n".join(output))
            self.assertEqual(ctx.users.count(), 1)

    def test_product_update_description_optional_and_delete(self):
        self.add_product()
        result = self.drive(["1", "admin01", "1", "3", "PRD001", "description", "",
                             "4", "PRD001", "y", "0", "0", "0"])
        self.assertIn("Produk berhasil diperbarui", result)
        self.assertIn("Produk berhasil dihapus", result)
        self.assertIsNone(self.ctx.repository.search("PRD001"))

    def test_staff_cannot_see_adjustment_option(self):
        self.make_user(Role.STAFF, "staff03")
        result = self.drive(["1", "staff03", "2", "0", "0", "0"])
        self.assertIn("MANAJEMEN STOK", result)
        self.assertNotIn("Penyesuaian stok (admin)", result)
