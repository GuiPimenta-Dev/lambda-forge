from infra.services import Services


class SignupConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="SignUp",
            path="./functions/auth",
            description="Securely handle user registration with unique credentials.",
            directory="signup",
            environment={
                "AUTH_TABLE_NAME": services.dynamodb.auth_table.table_name,
                "KMS_KEY_ID": services.kms.auth_key.key_id,
            },
        )

        services.api_gateway.create_endpoint("POST", "/signup", function, public=True)

        services.dynamodb.grant_write("auth_table", function)

        services.kms.auth_key.grant_encrypt(function)