from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:

        self.requests_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="RequestsLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p310-requests:12",
        )

        self.sm_utils_layer = _lambda.LayerVersion(
            scope,
            id="SmUtilsLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/sm_utils")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="",
        )
