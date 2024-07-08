from infra.services import Services


class SecretAuthorizerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="SecretAuthorizer",
            path="./authorizers/secret",
            description="An authorizer to validate requests based on a secret present on the headers",
        )

        services.api_gateway.create_authorizer(function, name="secret", default=True)
