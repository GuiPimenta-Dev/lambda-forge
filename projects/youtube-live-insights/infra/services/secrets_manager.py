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


{
    "video_id": "559484e7-09b8-4dc7-a55c-cc4e0e810814",
    "interval": 10,
    "min_messages": 5,
    "prompt": "Fernanda Kipper is a Brazilian content creator known for her insightful and educational videos on technology and programming. With a strong background in software development, she shares tutorials, tips, and career advice, helping her audience navigate the tech industry. Fernanda's channel is appreciated for its clear and approachable style, making complex topics accessible to beginners and experienced developers alike.",
}
