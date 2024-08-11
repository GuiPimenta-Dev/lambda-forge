from pathlib import Path
from typing import List, Optional


class ForgeAPI:
    _instance = None
    rows = []

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_servers(self) -> List[List[Optional[str]]]:
        return self.rows

    def set_functions(self, functions) -> None:
        for function in functions:
            row = (
                function["name"],
                function["service"],
                function["type"],
                function["trigger"],
            )
            self.rows.append(row)

    def get_log_file_path(self) -> Path:
        path = Path.home() / "live.log"
        if not path.exists():
            path.touch()

        return path
