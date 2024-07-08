from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:

        self.my_custom_layer = _lambda.LayerVersion(
            scope,
            id="MyCustomLayerLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/my_custom_layer")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="",
        )

        self.requests_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="RequestsLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:requests:2",
        )
