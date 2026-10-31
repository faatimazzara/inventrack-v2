from pathlib import Path

from inventrack.benchmark.benchmark_runner import BenchmarkResult
from inventrack.bootstrap import AppContext
from inventrack.cli.input_helpers import TerminalIO
from inventrack.cli.menus import login_menu
from inventrack.domain.exceptions import InventoryError
from inventrack.domain.user import User


class App:
    def __init__(self, ctx: AppContext, *, io: TerminalIO | None = None,
                 output_dir: Path | str = "outputs") -> None:
        self.ctx = ctx
        self.io = io if io is not None else TerminalIO()
        self.output_dir = Path(output_dir)
        self.user: User | None = None
        self.benchmark_results: list[BenchmarkResult] = []

    def safe(self, task) -> None:
        try:
            task()
        except (InventoryError, ValueError, OverflowError) as exc:
            self.io.say(f"[GAGAL] {exc}")

    def run(self) -> None:
        try:
            login_menu.run(self)
        except (KeyboardInterrupt, EOFError):
            self.io.say("\nProgram ditutup.")
