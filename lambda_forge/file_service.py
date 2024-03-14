import os
from pathlib import Path
import shutil
from importlib import resources


from typing import List


class FileService:

    root_dir = os.getcwd()

    def join(self, *args) -> str:
        return os.path.join(*args)

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

    def copy_folders(
        self, package_name: str, resource_name: str, destination: str
    ) -> None:
        with resources.path(package_name, resource_name) as src:
            dst = Path(self.root_dir + destination)

            for src_path in Path(src).glob("**/*"):
                if src_path.is_file():
                    dst_path = dst / src_path.relative_to(src)
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
