from infra.services import Services
import aws_cdk.aws_iam as iam


class ChartWorkerConfig:
    def __init__(self, services: Services, scope) -> None:

        function = services.aws_lambda.create_function(
            name="ChartWorker",
            path="./functions/chart",
            description="Worker to create the chart from the chat messages in background",
            directory="chart_worker",
            layers=[
                services.layers.sm_utils_layer,
                services.layers.openai_layer,
                services.layers.pydantic_klayers_layer,
            ],
            environment={
                "CHATS_TABLE_NAME": services.dynamodb.chats_table.table_name,
                "TRANSCRIPTIONS_TABLE_NAME": services.dynamodb.transcriptions_table.table_name,
                "OPENAPI_KEY_SECRET_NAME": services.secrets_manager.open_api_secret.secret_name,
            },
        )

        services.sqs.create_trigger("workers_queue", function)

        services.s3.large_payload_bucket.grant_read_write(function)

        comprehend_policy = iam.PolicyStatement(actions=["comprehend:*"], resources=["*"], effect=iam.Effect.ALLOW)

        function.role.attach_inline_policy(iam.Policy(scope, "ComprehendPolicy", statements=[comprehend_policy]))

        services.dynamodb.grant_write("transcriptions_table", function)
        services.dynamodb.chats_table.grant_read_data(function)

        services.secrets_manager.open_api_secret.grant_read(function)
