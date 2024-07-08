from aws_cdk import aws_secretsmanager as sm


class SecretsManager:
    def __init__(self, scope, context) -> None:

        self.gmail_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="GmailSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:mailer-TfIeka",
        )

        self.jwt_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="JwtSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:jwt-yx2zBV",
        )

        self.google_sso_secret = sm.Secret.from_secret_complete_arn(
            scope,
            id="GoogleSSOSecret",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:211125768252:secret:google-sso-cVVYlk",
        )
