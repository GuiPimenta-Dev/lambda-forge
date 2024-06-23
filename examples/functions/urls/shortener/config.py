from infra.services import Services


class ShortenerConfig:
    def __init__(self, services: Services, context) -> None:

        function = services.aws_lambda.create_function(
            name="Shortener",
            path="./functions/urls",
            description="Creates a new short URL entry in DynamoDB mapping to the original url",
            directory="shortener",
            environment={
                "URLS_TABLE_NAME": services.dynamodb.urls_table.table_name,
                "BASE_URL": context.resources["base_url"],
            },
        )

        services.api_gateway.create_endpoint("POST", "/urls", function, public=True)

        services.dynamodb.grant_write("urls_table", function)
