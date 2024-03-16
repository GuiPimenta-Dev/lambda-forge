import contextlib
import pytest
import shutil
import os


@pytest.fixture(scope="function", autouse=True)
def clean_project_structure():
    yield

    folders_to_delete = ["functions", "infra"]
    files_to_delete = [
        ".coveragerc",
        ".pre-commit-config.yaml",
        "cdk.context.json",
        "cdk.json",
        "conftest.py",
        "generate_docs.py",
        "pytest.ini",
        "app.py",
        "requirements.txt",
        "source.bat",
        "swagger_yml_to_ui.py",
        "validate_docs.py",
        "validate_integration_tests.py",
    ]

    for folder in folders_to_delete:
        shutil.rmtree(folder, ignore_errors=True)

    for file in files_to_delete:
        with contextlib.suppress(OSError):
            os.remove(file)


def file_exists(file_path):
    return os.path.exists(file_path)


def read_lines(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return []


def created_files(root_dir):
    ignore_dirs = [
        ".venv",
        "venv",
        ".pytest_cache",
        "__pycache__",
        ".git",
        ".vscode",
        "lambda_forge",
        "tests",
    ]
    ignore_files = ["LICENSE", "README.md", "setup.py", ".env", "clean.py", "deploy.py"]
    all_files = []
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # Remove directories in ignore_dirs from the traversal
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file not in ignore_files:
                all_files.append(os.path.join(root, file))
    return all_files
