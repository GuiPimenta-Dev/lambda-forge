from infra.services import Services


class ChartWorkerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="ChartWorker",
            path="./functions/chart",
            description="Worker to create the chart from the chat messages in background",
            directory="transcription_worker",
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

        services.dynamodb.grant_write("transcriptions_table", function)
        services.dynamodb.chats_table.grant_read_data(function)

        services.secrets_manager.open_api_secret.grant_read(function)
