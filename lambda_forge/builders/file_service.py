import os
import shutil
from importlib import resources
from pathlib import Path
from typing import List


class FileService:

    root_dir = os.getcwd()

    def join(self, *args) -> str:
        return os.path.join(*args)

    def file_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def make_dir(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def make_file(self, path: str, name, content: str = "") -> None:
        with open(os.path.join(path, name), "w") as f:
            f.write(content)

    def write_lines(self, path: str, lines: List) -> None:
        with open(path, "w") as f:
            for line in lines:
                f.write(line)

    def read_lines(self, path: str) -> List:
        with open(path, "r") as f:
            return f.readlines()

    def copy_file(
        self, package_name, resource_name: str, full_destination: str
    ) -> None:
        dst = Path(self.root_dir) / full_destination
        src = resources.files(package_name) / resource_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    def copy_folders(
        self, package_name: str, resource_name: str, destination: str
    ) -> None:
        dst = Path(self.root_dir) / destination
        src = resources.files(package_name) / resource_name
        dst.mkdir(parents=True, exist_ok=True)
        for src_path in src.glob("**/*"):
            if src_path.is_file():
                dst_path = dst / src_path.relative_to(src)
                dst_path.parent.mkdir(
                    parents=True, exist_ok=True
                )  # Ensure parent directory exists
                shutil.copy2(src_path, dst_path)
