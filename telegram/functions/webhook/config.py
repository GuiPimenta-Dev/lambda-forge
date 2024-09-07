from infra.services import Services


class WebhookConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Webhook",
            path="./functions/webhook",
            description="Lambda Forge telegram webhook",
            layers=[services.layers.requests_layer, services.layers.sm_utils_layer],
            environment={
                "MY_CHAT_ID": services.parameter_store.chat_id.string_value,
                "TELEGRAM_TABLE_NAME": services.dynamodb.telegram_table.table_name,
            },
        )

        services.api_gateway.create_endpoint("POST", "/webhook", function, public=True)

        services.secrets_manager.telegram_secret.grant_read(function)
        services.secrets_manager.authorizer_secret.grant_read(function)

        services.dynamodb.grant_write("telegram_table", function)
