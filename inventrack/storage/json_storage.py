import json
import os
import tempfile
from pathlib import Path
from typing import Any

from inventrack.domain.exceptions import StorageError


class JsonStorage:
    """Atomic JSON snapshots for a local single-process teaching prototype."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def read(self, default: Any) -> Any:
        if not self.path.exists():
            return default
        try:
            with self.path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError, UnicodeError) as exc:
            raise StorageError(f"Tidak dapat membaca {self.path}: {exc}") from exc

    def write(self, payload: Any) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=f".{self.path.stem}-", suffix=".tmp", delete=False
            ) as file:
                tmp_path = Path(file.name)
                json.dump(payload, file, indent=2, ensure_ascii=False)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            os.replace(tmp_path, self.path)
        except (OSError, TypeError, ValueError) as exc:
            if "tmp_path" in locals():
                tmp_path.unlink(missing_ok=True)
            raise StorageError(f"Tidak dapat menyimpan {self.path}: {exc}") from exc
