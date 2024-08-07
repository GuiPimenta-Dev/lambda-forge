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
        
        self.transcriptions_table = dynamodb.Table.from_table_arn(
            scope,
            "TranscriptionsTable",
            "arn:aws:dynamodb:us-east-2:211125768252:table/Prod-Live-Insights-Live-Transcriptions",
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
