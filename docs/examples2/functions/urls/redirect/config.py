from infra.services import Services


class RedirectConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Redirect",
            path="./functions/urls",
            description="Redirects from the short url to the original url",
            directory="redirect",
            environment={
                "URLS_TABLE_NAME": services.dynamodb.urls_table.table_name,
            },
        )

        services.api_gateway.create_endpoint("GET", "/{url_id}", function, public=True)

        services.dynamodb.urls_table.grant_read_data(function)
