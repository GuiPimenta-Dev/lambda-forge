import os
from pathlib import Path


class FileWatcher:
    def __init__(self, file_to_watch: Path):
        self.file_to_watch = file_to_watch
        self.last_modified_time = 0

    def get_modified_time(self):
        try:
            return os.path.getmtime(self.file_to_watch)
        except FileNotFoundError:
            return None

    def has_modified(self):
        current_modified_time = self.get_modified_time()
        if current_modified_time != self.last_modified_time:
            self.last_modified_time = current_modified_time
            return True
        return False

    def clear_file(self):
        with open(self.file_to_watch, "w") as f:
            f.write("")
