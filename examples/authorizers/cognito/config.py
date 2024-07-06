
from aws_cdk import aws_apigateway as apigateway


class CognitoAuthorizerConfig:
    def __init__(self, scope, services) -> None:

        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            scope, 'CognitoAuthorizer',
            cognito_user_pools=[services.cognito.blog_user_pool]
        )

        services.api_gateway.create_authorizer(authorizer, name="cognito", default=False)
