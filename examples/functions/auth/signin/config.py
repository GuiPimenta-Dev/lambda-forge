from infra.services import Services


class SigninConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Signin",
            path="./functions/auth",
            description="Authenticate user login by verifying email and password against stored credentials",
            directory="signin",
            layers=[services.layers.sm_utils_layer, services.layers.pyjwt_layer],
            environment={
                "AUTH_TABLE_NAME": services.dynamodb.auth_table.table_name,
                "KMS_KEY_ID": services.kms.auth_key.key_id,
                "JWT_SECRET_NAME": services.secrets_manager.jwt_secret.secret_name,
            },
        )

        services.api_gateway.create_endpoint("POST", "/signin", function, public=True)

        services.dynamodb.auth_table.grant_read_data(function)

        services.kms.auth_key.grant_decrypt(function)

        services.secrets_manager.jwt_secret.grant_read(function)