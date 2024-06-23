from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:

        self.qrcode_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="QrCodeLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:QRCode:1",
        )

        self.sm_utils_layer = _lambda.LayerVersion(
            scope,
            id="SmUtilsLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/sm_utils")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="",
        )

        self.pyjwt_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="JWTLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p39-PyJWT:3",
        )

        self.requests_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="RequestsLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p39-requests:19",
        )

        self.bs4_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="BS4Layer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p39-beautifulsoup4:7",
        )

        self.iot = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="IotLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:awsiot:1",
        )

        