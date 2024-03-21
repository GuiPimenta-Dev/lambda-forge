import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Context:
    stage: str
    name: str
    repo: dict
    bucket: str
    coverage: str
    resources: dict


def context(stage, resources):
    def decorator(func):
        cdk = json.load(open("cdk.json"))

        if resources not in cdk["context"]:
            raise ValueError(f"Resources {resources} not found in cdk.json")

        if "arns" not in cdk["context"][resources]:
            raise ValueError(f"Resources {resources} arns not found in cdk.json")

        name = cdk["context"]["name"]
        repo = cdk["context"]["repo"]
        bucket = cdk["context"]["bucket"]
        coverage = cdk["context"]["coverage"]

        context = Context(
            stage=stage.title().replace("_", "-").replace(" ", "-"),
            name=name,
            repo=repo,
            bucket=bucket,
            coverage=coverage,
            resources=cdk["context"][resources],
        )

        def wrapper(*args, **kwargs):
            return func(context=context, *args, **kwargs)

        return wrapper

    return decorator
