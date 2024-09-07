from infra.services import Services


class TextualConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Textual",
            path="./functions/rag",
            directory="textual",
            description="Lambda Forge telegram webhook for Textual",
            layers=[services.layers.requests_layer, services.layers.sm_utils_layer],
        )

        services.api_gateway.create_endpoint("POST", "/textual", function, public=True)

        services.secrets_manager.textual_telegram_secret.grant_read(function)
        services.secrets_manager.authorizer_secret.grant_read(function)

