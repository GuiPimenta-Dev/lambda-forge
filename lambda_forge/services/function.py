from aws_cdk import Duration
from aws_cdk.aws_lambda import Code
from aws_cdk.aws_lambda import Function as AWSFunction

from lambda_forge.path import Path
from lambda_forge.trackers import function


class Function:
    def __init__(self, scope, context) -> None:
        self.functions = {}
        self.scope = scope
        self.context = context

    @function
    def create_function(
        self,
        name,
        path,
        description,
        timeout,
        directory,
        layers,
        environment,
        memory_size,
        runtime,
    ):

        function = AWSFunction(
            scope=self.scope,
            id=name,
            description=description,
            function_name=self.context.gen_id(name),
            runtime=runtime,
            handler=Path.handler(directory),
            environment=environment,
            code=Code.from_asset(path=Path.function(path)),
            layers=layers,
            timeout=Duration.minutes(timeout),
            memory_size=memory_size,
        )

        self.functions[name] = function
        return function
