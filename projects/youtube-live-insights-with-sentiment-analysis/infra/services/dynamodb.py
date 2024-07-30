from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_event_sources as event_source

from lambda_forge.trackers import invoke, trigger


class DynamoDB:
    def __init__(self, scope, context) -> None:

        self.videos_table = dynamodb.Table.from_table_arn(
            scope,
            "VideosTable",
            context.resources["arns"]["videos_table_arn"],
        )

        self.chats_table = dynamodb.Table.from_table_arn(
            scope,
            "ChatsTable",
            context.resources["arns"]["chats_table_arn"],
        )

        self.transcriptions_table = dynamodb.Table(
            scope,
            "TranscriptionsTable",
            table_name=f"{context.stage}-{context.name}-Live-Transcriptions",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
        )

    @trigger(service="dynamodb", trigger="table", function="function")
    def create_trigger(self, table: str, function: lambda_.Function) -> None:
        table_instance = getattr(self, table)
        dynamo_event_stream = event_source.DynamoEventSource(
            table_instance, starting_position=lambda_.StartingPosition.TRIM_HORIZON
        )
        function.add_event_source(dynamo_event_stream)

    @invoke(service="dynamodb", resource="table", function="function")
    def grant_write(self, table: str, function: lambda_.Function) -> None:
        table_instance = getattr(self, table)
        table_instance.grant_write_data(function)
