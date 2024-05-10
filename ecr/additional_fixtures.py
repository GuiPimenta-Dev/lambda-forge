import json


def pytest_html_report_title(report):
    report.title = "Test Report"


def pytest_generate_tests(metafunc):
    for mark in metafunc.definition.iter_markers(name="integration"):
        with open("tested_endpoints.txt", "a") as f:
            f.write(f"{json.dumps(mark.kwargs)}|")
