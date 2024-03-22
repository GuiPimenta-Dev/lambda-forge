from infra.services import Services

class DocsConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Docs",
            path="./functions/authorizers",
            description="Function used to authorize the docs endpoints",
            directory="docs"
        )

        services.api_gateway.create_authorizer(function, name="docs", default=False)
