import json
import pathlib

import attrs


@attrs.frozen
class JSONRepositoryMixin:
    database_file: pathlib.Path

    def _read_database(self) -> dict:
        self._maybe_init_database()
        with open(self.database_file, "r") as f:
            return json.load(f)

    def _write_database(self, data: dict) -> None:
        with open(self.database_file, "w") as f:
            json.dump(data, f, indent=2)

    def _maybe_init_database(self) -> None:
        if self.database_file.is_file():
            return None

        data: dict[str, list] = {
            "lesson_plans": [],
            "exercises": [],
        }

        with open(self.database_file, "x") as f:
            json.dump(data, f)
