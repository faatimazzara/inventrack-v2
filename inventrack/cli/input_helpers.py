from decimal import Decimal, InvalidOperation
from getpass import getpass
from typing import Callable

from inventrack.domain.exceptions import ValidationError


class TerminalIO:
    """Injectable IO makes all menu flows independently testable."""

    def __init__(self, read: Callable[[str], str] = input,
                 password: Callable[[str], str] = getpass,
                 write: Callable[[str], None] = print) -> None:
        self._read, self._password, self._write = read, password, write

    def say(self, value: object = "") -> None:
        self._write(str(value))

    def ask(self, prompt: str, *, required: bool = True) -> str:
        value = self._read(prompt).strip()
        if required and not value:
            raise ValidationError("Input tidak boleh kosong.")
        return value

    def secret(self, prompt: str = "Password: ") -> str:
        return self._password(prompt)

    def integer(self, prompt: str, *, minimum: int = 0) -> int:
        raw = self.ask(prompt)
        if not raw.isdecimal():
            raise ValidationError("Masukkan bilangan bulat yang valid.")
        value = int(raw)
        if value < minimum:
            raise ValidationError(f"Nilai minimal adalah {minimum}.")
        return value

    def decimal(self, prompt: str) -> Decimal:
        try:
            return Decimal(self.ask(prompt))
        except InvalidOperation as exc:
            raise ValidationError("Masukkan angka harga yang valid.") from exc

    def yes(self, prompt: str = "Yakin? (y/t): ") -> bool:
        return self.ask(prompt).lower() == "y"

    def menu(self, title: str, options: dict[str, str], back: str = "Kembali") -> str:
        self.say("\n" + "=" * 54)
        self.say(title)
        self.say("=" * 54)
        for key, description in options.items():
            self.say(f"{key}. {description}")
        self.say(f"0. {back}")
        return self._read("Pilih menu: ").strip()


def show_products(io: TerminalIO, products: list) -> None:
    if not products:
        io.say("Tidak ada produk.")
        return
    io.say(f"{'ID':<13} {'Nama':<23} {'Kategori':<15} {'Stok':>6} {'Harga':>14}  Status")
    io.say("-" * 92)
    for p in products:
        io.say(f"{p.product_id:<13} {p.name[:22]:<23} {p.category[:14]:<15} "
               f"{p.stock:>6} {str(p.price):>14}  {p.stock_status}")


def show_product(io: TerminalIO, p) -> None:
    for label, val in (("ID", p.product_id), ("Nama", p.name),
                       ("Kategori", p.category), ("Merek", p.brand),
                       ("Harga (Rp)", p.price), ("Stok", p.stock),
                       ("Stok minimum", p.minimum_stock),
                       ("Status stok", p.stock_status), ("Deskripsi", p.description),
                       ("Dibuat", p.created_at), ("Diperbarui", p.updated_at)):
        io.say(f"{label:<15}: {val}")
