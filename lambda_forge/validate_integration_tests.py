import json
import os


def validate_tests(endpoints, tested_endpoints):
    for endpoint in endpoints:
        if endpoint not in tested_endpoints:
            raise Exception(
                f"Endpoint {endpoint['endpoint']} with method {endpoint['method']} should have at least 1 integration test."
            )


if __name__ == "__main__":

    tested_endpoints = []
    if os.path.exists(".tested_endpoints.jsonl"):
        with open(".tested_endpoints.jsonl", "r") as jl:
            json_list = list(jl)
            tested_endpoints = [json.loads(json_str) for json_str in json_list]

    with open("cdk.json", "r") as json_file:
        context = json.load(json_file)["context"]
        functions = context["functions"]

    endpoints = [endpoint for endpoint in functions if "method" in endpoint]
    validate_tests(endpoints, tested_endpoints)
