import json


def list_lambda_functions():
    with open("functions.json") as f:
        functions = json.load(f)
        pre = "Lambda-Forge-Demo-"
        function_names = [pre + i["name"] for i in functions]
        return function_names
