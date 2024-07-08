from infra.services import Services


class GetChatConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="GetChat",
            path="./functions/download",
            directory="get_chat",
            description="Get Live chat messages and stores on DynamoDB",
            timeout=15,
            memory_size=512,
            layers=[services.layers.chat_downloader_layer],
            environment={
                "CHATS_TABLE_NAME": services.dynamodb.chats_table.table_name,
            },
        )

        services.sns.create_trigger("videos_topic", function)

        services.dynamodb.grant_write("chats_table", function)
