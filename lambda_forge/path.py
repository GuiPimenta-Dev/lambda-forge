import shutil
import tempfile
import os


class Path:
    _instance = None
    _temp_dir = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Path, cls).__new__(cls)
            cls._temp_dir = tempfile.mkdtemp()
        return cls._instance

    @staticmethod
    def handler(directory):
        return f"src.{directory}.main.lambda_handler" if directory else "src.main.lambda_handler"
    
    @staticmethod
    def function(src):
        if Path._temp_dir is None:
            Path()

        # Adjust the path to be relative to the temporary directory
        relative_path = src.split("functions/")[1] if "functions/" in src else src
        destination_path = os.path.join(Path._temp_dir, relative_path)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Copy the source directory to the destination
        shutil.copytree(src, f"{destination_path}/src", dirs_exist_ok=True)

        return destination_path

    @staticmethod
    def layer(path):
        if Path._temp_dir is None:
            Path()

        # Adjust the path to be relative to the temporary directory
        destination_path = os.path.join(Path._temp_dir, path)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Copy the source directory to the destination
        shutil.copytree(path, f"{destination_path}/python", dirs_exist_ok=True)

        return destination_path