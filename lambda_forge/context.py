import json

from lambda_forge.trackers import reset


class Context:
    def __init__(self, stage, name, repo, region, account, bucket, resources, minimal) -> None:
        self.stage = stage
        self.name = name
        self.repo = repo
        self.region = region
        self.account = account
        self.bucket = bucket
        self.resources = resources
        self.minimal = minimal

    def create_id(self, resource):
        if self.minimal:
            return f"{self.name}-{resource}"

        return f"{self.stage}-{self.name}-{resource}"

    def __str__(self):
        return f"Context(stage='{self.stage}', name='{self.name}', repo='{self.repo}', region='{self.region}', account='{self.account}', bucket='{self.bucket}', resources='{self.resources}', minimal='{self.minimal}')"

    def __repr__(self):
        return f"Context(stage='{self.stage}', name='{self.name}', repo='{self.repo}', region='{self.region}', account='{self.account}', bucket='{self.bucket}', resources='{self.resources}', minimal='{self.minimal}')"


def create_context(stage, resources, minimal):
    cdk = json.load(open("cdk.json"))

    if minimal:

        stage = "Prod"

        if "resources" not in cdk["context"]:
            raise ValueError(f"Resources not found in cdk.json")

        resources = cdk["context"]["resources"]

    else:

        if resources not in cdk["context"]:
            raise ValueError(f"Resources {resources} not found in cdk.json")

        if "arns" not in cdk["context"][resources]:
            raise ValueError(f"Resources {resources} arns not found in cdk.json")

        resources = cdk["context"][resources]

    name = cdk["context"]["name"]
    repo = cdk["context"]["repo"]
    region = cdk["context"]["region"]
    account = cdk["context"]["account"]
    bucket = cdk["context"]["bucket"]

    context = Context(
        stage=stage,
        name=name,
        repo=repo,
        region=region,
        account=account,
        bucket=bucket,
        resources=resources,
        minimal=minimal,
    )

    return context


def context(stage=None, resources=None, minimal=False, **decorator_kwargs):
    def decorator(func):
        @reset
        def wrapper(*func_args, **func_kwargs):
            context = create_context(stage, resources, minimal)
            return func(context=context, *func_args, **func_kwargs)

        return wrapper

    return decorator
