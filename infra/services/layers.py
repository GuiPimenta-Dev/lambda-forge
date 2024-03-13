from aws_cdk import aws_lambda as _lambda


class Layers:
    def __init__(self, scope) -> None:

        self.requests_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="requests_layer",
            layer_version_arn="",
        )
