from infra.services import Services


class SwaggerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Swagger",
            path="./functions/docs",
            description="A function used to authorize the docs",
            directory="swagger",
        )

        services.api_gateway.create_authorizer(function, name="docs_authorizer")
