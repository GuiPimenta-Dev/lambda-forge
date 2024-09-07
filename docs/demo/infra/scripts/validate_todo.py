import json
import os


def check_functions_for_todo(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)

    functions = data.get("functions", [])

    for function in functions:
        path = function.get("path", "")
        with open(path, "r") as file:
            if "# TODO" in file.read():
                raise ValueError(f"TODO found in file: {path}")

    print("No TODO found in any files.")


if __name__ == "__main__":
    json_file_path = "cdk.json"
    check_functions_for_todo(json_file_path)
