"""InvenTrack v2.0 CLI entry point. Run with: python main.py"""
import argparse
from pathlib import Path

from inventrack.bootstrap import bootstrap
from inventrack.cli.app import App
from inventrack.config import DEFAULT_DATA_DIR, PROJECT_ROOT
from inventrack.domain.exceptions import InventoryError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="InvenTrack v2.0 — Inventory Management")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR,
                        help="Folder penyimpanan JSON (default: ./data)")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "outputs",
                        help="Folder laporan benchmark CSV")
    args = parser.parse_args(argv)
    try:
        App(bootstrap(args.data_dir), output_dir=args.output_dir).run()
        return 0
    except (InventoryError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f"[ERROR] Gagal memulai InvenTrack: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
