from infra.services import Services


class CognitoAuthorizerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CognitoSSOAuthorizer",
            path="./authorizers/cognito",
            description="A cognito authorizer for private lambda functions",
            layers=[services.layers.pyjwt_layer],
        )

        services.api_gateway.create_authorizer(function, name="cognito", default=False)
