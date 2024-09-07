from infra.services import Services


class JwtAuthorizerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="JwtAuthorizer",
            path="./authorizers/jwt",
            description="A jwt authorizer for private lambda functions",
            layers=[services.layers.sm_utils_layer, services.layers.pyjwt_layer],
            environment={
                "JWT_SECRET_NAME": services.secrets_manager.jwt_secret.secret_name
            },
        )

        services.api_gateway.create_authorizer(function, name="jwt", default=False)

        services.secrets_manager.jwt_secret.grant_read(function)
