from aws_cdk import aws_cognito as cognito


class Cognito:
    def __init__(self, scope, context) -> None:

        self.blog_user_pool = cognito.UserPool.from_user_pool_arn(
            scope,
            f"{context.stage}-blog-user-pool",
            "arn:aws:cognito-idp:us-east-2:211125768252:userpool/us-east-2_JKQ7WdFVv",
        )
