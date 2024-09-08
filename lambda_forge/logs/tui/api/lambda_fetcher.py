import json
from typing import List, Optional


def list_lambda_functions(project_name: Optional[str]) -> List[str]:

    if project_name:
        project_name = project_name + "-"
    else:
        project_name = ""

    with open("functions.json") as f:
        functions = json.load(f)
        function_names = [project_name + i["name"] for i in functions]
        return function_names
