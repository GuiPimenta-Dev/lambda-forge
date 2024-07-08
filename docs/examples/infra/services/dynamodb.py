from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_event_sources as event_source
from lambda_forge.trackers import invoke, trigger


class DynamoDB:
    def __init__(self, scope, context) -> None:

        self.numbers_table = dynamodb.Table.from_table_arn(
            scope,
            "NumbersTable",
            context.resources["arns"]["numbers_table"],
        )

        self.urls_table = dynamodb.Table.from_table_arn(
            scope,
            "UrlsTable",
            context.resources["arns"]["urls_table"],
        )

        self.auth_table = dynamodb.Table.from_table_arn(
            scope,
            "AuthTable",
            context.resources["arns"]["auth_table"],
        )

        self.books_table = dynamodb.Table.from_table_arn(
            scope,
            "BooksTable",
            "arn:aws:dynamodb:us-east-2:211125768252:table/Books",
        )

        self.posts_table = dynamodb.Table.from_table_arn(
            scope,
            "PostsTable",
            "arn:aws:dynamodb:us-east-2:211125768252:table/Dev-Blog-Posts",
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
