import contextlib
import shutil
import os


def clean_project_structure():

    folders_to_delete = ["functions", "infra", ".fc"]
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
        ".tested_endpoints.jsonl",
        "docs.yaml",
    ]

    for folder in folders_to_delete:
        shutil.rmtree(folder, ignore_errors=True)

    for file in files_to_delete:
        with contextlib.suppress(OSError):
            os.remove(file)


if __name__ == "__main__":
    clean_project_structure()
