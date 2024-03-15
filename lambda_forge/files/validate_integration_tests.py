import json
import os

import aws_cdk as cdk

from infra.stacks.lambda_stack import LambdaStack

with open("cdk.json", "r") as json_file:
    context = json.load(json_file)["context"]
    arns = context["dev"]["arns"]

tested_endpoints = []

if os.path.exists("tested_endpoints.jsonl"):
    with open("tested_endpoints.jsonl", "r") as jl:
        json_list = list(jl)
        tested_endpoints = [json.loads(json_str) for json_str in json_list]

services = LambdaStack(
    cdk.App(),
    "Dev",
    arns,
).services

functions = services.aws_lambda.functions
api_endpoints = services.api_gateway.endpoints

endpoints = []

for function in functions:
    function_name = function["name"]
    if function_name in api_endpoints:
        endpoint = api_endpoints[function_name]["endpoint"]
        method = api_endpoints[function_name]["method"]
        merged_obj = {
            "file_path": function["file_path"],
            "name": function_name,
            "description": function["description"],
            "endpoint": endpoint,
            "method": method,
        }
        endpoints.append(merged_obj)

endpoints = [
    {"method": endpoint["method"], "endpoint": endpoint["endpoint"]}
    for endpoint in endpoints
]

for endpoint in endpoints:
    if endpoint not in tested_endpoints:
        raise Exception(
            f"Endpoint {endpoint['endpoint']} with method {endpoint['method']} should have at least 1 integration test."
        )
