from aws_cdk import Duration
from aws_cdk.aws_lambda import Code, Function, Runtime
from lambda_forge.path import Path
from lambda_forge.trackers import function


class Lambda:
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
        directory=None,
        layers=[],
        environment={},
        memory_size=128,
        runtime=Runtime.PYTHON_3_9,
        timeout=1,
        dead_letter_queue_enabled=False,
        dead_letter_queue=None,
    ):

        function = Function(
            scope=self.scope,
            id=name,
            description=description,
            function_name=self.context.create_id(name),
            runtime=runtime,
            handler=Path.handler(directory),
            environment=environment,
            code=Code.from_asset(path=Path.function(path)),
            layers=layers,
            timeout=Duration.minutes(timeout),
            memory_size=memory_size,
            dead_letter_queue_enabled=dead_letter_queue_enabled,
            dead_letter_queue=dead_letter_queue,
        )

        self.functions[name] = function
        return function
