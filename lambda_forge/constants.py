import json
from typing import NamedTuple


def get_base_url():
    with open("cdk.json") as f:
        return json.load(f)["context"]["base_url"]


BASE_URL = get_base_url()


class ECR(NamedTuple):
    LATEST = "public.ecr.aws/w1u4u5r2/lambda-forge:latest"
