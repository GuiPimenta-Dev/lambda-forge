import shutil

from aws_cdk import Duration
from aws_cdk.aws_lambda import Code, Function, Runtime


class AWSLambda:
    def __init__(self, scope, stage) -> None:
        self.scope = scope
        self.stage = stage
        self.functions = []

    def create_function(
        self,
        name,
        path,
        description,
        directory=None,
        timeout=Duration.minutes(1),
        layers=[],
        environment={},
    ):
        repo_name = self.scope.node.try_get_context("name")
        handler = (
            f"src.{directory}.main.lambda_handler"
            if directory
            else "src.main.lambda_handler"
        )
        function = Function(
            scope=self.scope,
            id=name,
            description=description,
            function_name=f"{self.stage}-{repo_name}-{name}",
            runtime=Runtime.PYTHON_3_9,
            handler=handler,
            environment=environment,
            code=Code.from_asset(path=self.__top_level_path(path)),
            layers=layers,
            timeout=timeout,
        )

        return function

    @staticmethod
    def __top_level_path(src):
        path = f"./.fc/{src.split('functions/')[1]}"
        shutil.copytree(src, f"{path}/src", dirs_exist_ok=True)
        return path
