from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:

        self.bs4_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="BS4Layer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p310-beautifulsoup4:3",
        )

        self.requests_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="RequestsLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p310-requests:12",
        )
