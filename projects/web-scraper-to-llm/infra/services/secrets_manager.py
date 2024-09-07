from aws_cdk import aws_secretsmanager as sm


class SecretsManager:
    def __init__(self, scope, context) -> None:

        self.openai_api_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="OpenAIAPISecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:OPEN_API_KEY-GNmiVG",
        )

        self.pinecone_api_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="PineconeSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:PINECONE_API_KEY-amg8Im",
        )

        self.authorizer_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="AuthorizerSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:youtube-live-insights-zgUYte",
        )

        self.textual_telegram_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="TextualTelegramSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:TEXTUAL-TELEGRAM-TOKEN-1n6ypV",
        )