from infra.services import Services

class DocsAuthorizerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="DocsAuthorizer",
            path="./authorizers/docs",
            description="Function used to authorize the docs endpoints"
        )

        services.api_gateway.create_authorizer(function, name="docs", default=False)
