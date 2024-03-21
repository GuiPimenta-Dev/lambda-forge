from aws_cdk import Duration
from aws_cdk.aws_lambda import Code, Function, Runtime
from lambda_forge import Path


class AWSLambda:
    def __init__(self, scope, context) -> None:
        self.scope = scope
        self.context = context

    def create_function(
        self,
        name,
        path,
        description,
        directory=None,
        timeout=1,
        layers=[],
        environment={},
    ):
        handler = (
            f"src.{directory}.main.lambda_handler"
            if directory
            else "src.main.lambda_handler"
        )
        function = Function(
            scope=self.scope,
            id=name,
            description=description,
            function_name=f"{self.context.stage}-{self.context.name}-{name}",
            runtime=Runtime.PYTHON_3_9,
            handler=handler,
            environment=environment,
            code=Code.from_asset(path=Path.file(path)),
            layers=layers,
            timeout=Duration.minutes(timeout),
        )

        return function
