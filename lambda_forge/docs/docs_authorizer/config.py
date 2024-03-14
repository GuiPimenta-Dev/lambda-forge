from infra.services import Services


class DocsAuthorizerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="DocsAuthorizer",
            path="./functions/authorizer",
            description="A function used to authorize the docs",
            directory="docs_authorizer",
        )

        services.api_gateway.create_authorizer(function, name="docs_authorizer")
