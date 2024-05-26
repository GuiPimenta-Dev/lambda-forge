from aws_cdk import aws_cognito as cognito


class Cognito:
    def __init__(self, scope, context) -> None:

        # self.cognito = cognito.UserPool.from_user_pool_arn(
        #     scope,
        #     "Cognito",
        #     user_pool_arn=context.resources["arns"]["cognito_arn"],
        # )
        ...
