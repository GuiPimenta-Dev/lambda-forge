from aws_cdk import aws_dynamodb as dynamo_db
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_event_sources as event_source

from lambda_forge.trackers import invoke, trigger


class NoSQL:
    def __init__(self, scope, context) -> None:
        self.scope = scope
        self.context = context

    @trigger(service="dynamodb", trigger="table", function="function")
    def create_trigger(self, table, function):
        table = getattr(self, table)
        dynamo_event_stream = event_source.DynamoEventSource(
            table, starting_position=lambda_.StartingPosition.TRIM_HORIZON
        )
        function.add_event_source(dynamo_event_stream)

    @invoke(service="dynamodb", resource="table", function="function")
    def grant_write(self, table, function):
        table = getattr(self, table)
        table.grant_write_data(function)

    def grant_read(self, table, function):
        table = getattr(self, table)
        table.grant_read_data(function)

    def add_query_permission(self, table, function):
        table = getattr(self, table)
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=[f"{table.table_arn}/index/*"],
            )
        )

    def create_table(
        self,
        name,
        pk="PK",
        pk_type=dynamo_db.AttributeType.STRING,
        sk="SK",
        sk_type=dynamo_db.AttributeType.STRING,
        billing_mode=dynamo_db.BillingMode.PAY_PER_REQUEST,
    ):
        return dynamo_db.Table(
            self.scope,
            name,
            table_name=self.context.gen_id(name),
            partition_key=dynamo_db.Attribute(name=pk, type=pk_type),
            sort_key=dynamo_db.Attribute(name=sk, type=sk_type),
            billing_mode=billing_mode,
        )
