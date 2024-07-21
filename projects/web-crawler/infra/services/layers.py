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

        self.sm_utils_layer = _lambda.LayerVersion(
            scope,
            id="SmUtilsLayer",
            code=_lambda.Code.from_asset(Path.layer("layers/sm_utils")),
            description="",
        )

        self.open_ai_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="OpenAiLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p310-openai:7",
        )

        self.tiktoken_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="TikTokenLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:tiktoken-layer:4",
        )

        self.pinecone_client_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="PineconeClientLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:pinecone-client-layer:1",
        )

        self.langchain_all_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="LangchainAllLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:langchain-all-layer:1",
        )
