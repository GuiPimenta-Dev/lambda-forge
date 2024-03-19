import json


def pytest_generate_tests(metafunc):
    for mark in metafunc.definition.iter_markers(name="integration"):
        with open(".tested_endpoints.jsonl", "a") as f:
            f.write(f"{json.dumps(mark.kwargs)}\n")
