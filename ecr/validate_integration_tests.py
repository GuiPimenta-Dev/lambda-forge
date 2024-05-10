import json
import os


def validate_tests(endpoints, tested_endpoints):
    for endpoint in endpoints:
        new_endpoint = {"endpoint": endpoint["endpoint"], "method": endpoint["method"]}
        if new_endpoint not in tested_endpoints:
            raise Exception("Endpoint " + endpoint["endpoint"] + " with method " + endpoint["method"] + " should have at least 1 integration test.")


if __name__ == "__main__":

    tested_endpoints = []
    if os.path.exists("tested_endpoints.txt"):
        with open("tested_endpoints.txt", "r") as jl:
            json_list = jl.read().split("|")[:-1]
            tested_endpoints = [json.loads(json_str) for json_str in json_list]

    with open("cdk.json", "r") as json_file:
        context = json.load(json_file)["context"]
        functions = context["functions"]

    endpoints = [endpoint for endpoint in functions if "method" in endpoint]
    validate_tests(endpoints, tested_endpoints)
