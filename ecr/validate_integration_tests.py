import json
import os


def validate_tests(endpoints, tested_endpoints):
    for endpoint in endpoints:
        new_endpoint = {"endpoint": endpoint["trigger"], "method": endpoint["method"]}
        if new_endpoint not in tested_endpoints:
            raise Exception(
                f"Endpoint {endpoint['trigger']} with method {endpoint['method']} should have at least 1 integration test."
            )


if __name__ == "__main__":

    tested_endpoints = []
    if os.path.exists("tested_endpoints.txt"):
        with open("tested_endpoints.txt", "r") as jl:
            json_list = jl.read().split("|")[:-1]
            tested_endpoints = [json.loads(json_str) for json_str in json_list]

    with open("functions.json", "r") as json_file:
        functions = json.load(json_file)
        endpoints = []
        for function in functions:
            for trigger in function["triggers"]:
                if trigger["service"] == "api_gateway":
                    endpoints.append(trigger)

    validate_tests(endpoints, tested_endpoints)
