import json
from dataclasses import asdict, make_dataclass


class Context:
    stage: str
    name: str
    repo: dict
    region: str
    account: str
    bucket: str
    coverage: str
    resources: dict

    def gen_id(self, resource):
        return f"{self.stage}-{self.name}-{resource}"


def dict_to_dataclass(class_name, data_dict):
    keys = data_dict.keys()
    fields = [(key, data_dict[key]) for key in keys]
    return make_dataclass(class_name, fields)


def create_context(stage, resources):
    cdk = json.load(open("cdk.json"))

    if resources not in cdk["context"]:
        raise ValueError(f"Resources {resources} not found in cdk.json")

    if "arns" not in cdk["context"][resources]:
        raise ValueError(f"Resources {resources} arns not found in cdk.json")

    name = cdk["context"]["name"]
    repo = cdk["context"]["repo"]
    region = cdk["context"]["region"]
    account = cdk["context"]["account"]
    bucket = cdk["context"]["bucket"]
    coverage = cdk["context"]["coverage"]

    context = Context(
        stage=stage.title().replace("_", "-").replace(" ", "-"),
        name=name,
        repo=repo,
        region=region,
        account=account,
        bucket=bucket,
        coverage=coverage,
        resources=cdk["context"][resources],
    )

    return context


def context(stage, resources, **decorator_kwargs):
    def decorator(func):
        def wrapper(*func_args, **func_kwargs):
            kwargs = {**decorator_kwargs, **func_kwargs}
            context = create_context(stage, resources)
            input_dict = {**asdict(context), **kwargs}
            context = dict_to_dataclass("Context", input_dict)
            context = context(**input_dict)
            return func(context=context, *func_args, **func_kwargs)

        return wrapper

    return decorator
