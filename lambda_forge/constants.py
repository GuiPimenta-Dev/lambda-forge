import json


def get_base_url():
    with open("cdk.json") as f:
        return json.load(f)["context"]["base_url"]


BASE_URL = get_base_url()
