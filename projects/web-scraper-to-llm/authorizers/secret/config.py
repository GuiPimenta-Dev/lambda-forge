from infra.services import Services


class SecretAuthorizerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="SecretAuthorizer",
            path="./authorizers/secret",
            description="An authorizer based on a secret",
            layers=[services.layers.sm_utils_layer],
            environment={
                "AUTHORIZER_SECRET_NAME": services.secrets_manager.authorizer_secret.secret_name,
            },
        )

        services.api_gateway.create_authorizer(function, name="secret", default=True)

        services.secrets_manager.authorizer_secret.grant_read(function)
