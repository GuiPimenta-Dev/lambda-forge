from aws_cdk import Duration
from aws_cdk.aws_lambda import Code, Function, Runtime

from lambda_forge.trackers import track
from lambda_forge import Path


class Lambda:
    def __init__(self, scope, context) -> None:
        self.scope = scope
        self.context = context
        self.functions = {}

    @track
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

        function = Function(
            scope=self.scope,
            id=name,
            description=description,
            function_name=f"{self.context.stage}-{self.context.name}-{name}",
            runtime=Runtime.PYTHON_3_9,
            handler=Path.handler(directory),
            environment=environment,
            code=Code.from_asset(path=Path.function(path)),
            layers=layers,
            timeout=Duration.minutes(timeout),
        )

        self.functions[name] = function
        return function
