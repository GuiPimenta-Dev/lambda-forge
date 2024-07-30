from aws_cdk import aws_secretsmanager as sm


class SecretsManager:
    def __init__(self, scope, context) -> None:

        self.open_api_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="OpenAPISecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:OPEN_API_KEY-GNmiVG",
        )

        self.authorizer_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="AuthorizerSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:youtube-live-insights-zgUYte",
        )
