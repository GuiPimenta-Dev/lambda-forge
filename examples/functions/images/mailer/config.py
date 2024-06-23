from infra.services import Services


class MailerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Mailer",
            path="./functions/images",
            description="Sends an email when an image enters the bucket",
            directory="mailer",
            layers=[services.layers.sm_utils_layer],
            environment={
                "SMTP_HOST": "smtp.gmail.com",
                "SMTP_PORT": "465",
                "SECRET_NAME": services.secrets_manager.gmail_secret.secret_name,
            },
        )

        services.s3.images_bucket.grant_read(function)
        services.s3.create_trigger("images_bucket", function)

        services.secrets_manager.gmail_secret.grant_read(function)
