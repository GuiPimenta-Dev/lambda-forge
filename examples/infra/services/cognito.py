from aws_cdk import Duration
from aws_cdk import aws_cognito as cognito


class Cognito:
    def __init__(self, scope, context) -> None:
        
        # Define the User Pool
        self.blog_user_pool = cognito.UserPool(scope, f"{context.stage}-blog-user-pool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            standard_attributes=cognito.StandardAttributes(
                phone_number=cognito.StandardAttribute(required=False)
            ),
            email=cognito.UserPoolEmail.with_ses(
                ses_region="us-west-2",
                from_email="no-reply@test.com",
                from_name="Test Sender"
            )
        )

        # Define callback URLs
        callback_urls = [f"https://{context.stage}.test.com", "http://localhost:3000"]
        # Define the User Pool Client
        pool_client = self.blog_user_pool.add_client(f"{context.stage}-blog-client",
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True
                ),
                callback_urls=callback_urls
            ),
            id_token_validity=Duration.hours(8),
            access_token_validity=Duration.hours(8)
        )