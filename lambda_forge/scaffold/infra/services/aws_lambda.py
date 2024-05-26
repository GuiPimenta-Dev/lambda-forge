from aws_cdk import Duration
from aws_cdk.aws_lambda import Runtime

from lambda_forge.services import Function


class Lambda(Function):
    def __init__(self, scope, context) -> None:
        super().__init__(scope=scope, context=context)

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
        timeout=Duration.minutes(1),
    ):

        return super().create_function(
            name=name,
            path=path,
            description=description,
            directory=directory,
            layers=layers,
            environment=environment,
            memory_size=memory_size,
            runtime=runtime,
            timeout=timeout,
        )
