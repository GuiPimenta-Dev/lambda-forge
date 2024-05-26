from typing import Any, Optional
from aws_cdk import aws_dynamodb as dynamo_db
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_event_sources as event_source

from lambda_forge.trackers import invoke, trigger

class NoSQL:
    def __init__(self, scope: Any, context: Any) -> None:
        """
        Initialize the NoSQL service.

        Args:
            scope (Any): The scope within which this resource is defined.
            context (Any): The context containing configuration and environment details.
        """
        self.scope = scope
        self.context = context

    @trigger(service="dynamodb", trigger="table", function="function")
    def create_trigger(self, table: str, function: lambda_.Function) -> None:
        """
        Create a trigger on the DynamoDB table to invoke a Lambda function.

        Args:
            table (str): The name of the table.
            function (lambda_.Function): The Lambda function to be triggered.
        """
        table_instance = getattr(self, table)
        dynamo_event_stream = event_source.DynamoEventSource(
            table_instance, starting_position=lambda_.StartingPosition.TRIM_HORIZON
        )
        function.add_event_source(dynamo_event_stream)

    @invoke(service="dynamodb", resource="table", function="function")
    def grant_write(self, table: str, function: lambda_.Function) -> None:
        """
        Grant write permissions on the DynamoDB table to the specified Lambda function.

        Args:
            table (str): The name of the table.
            function (lambda_.Function): The Lambda function to be granted write permissions.
        """
        table_instance = getattr(self, table)
        table_instance.grant_write_data(function)

    def grant_read(self, table: str, function: lambda_.Function) -> None:
        """
        Grant read permissions on the DynamoDB table to the specified Lambda function.

        Args:
            table (str): The name of the table.
            function (lambda_.Function): The Lambda function to be granted read permissions.
        """
        table_instance = getattr(self, table)
        table_instance.grant_read_data(function)

    def add_query_permission(self, table: str, function: lambda_.Function) -> None:
        """
        Add query permissions to the specified Lambda function for the DynamoDB table.

        Args:
            table (str): The name of the table.
            function (lambda_.Function): The Lambda function to be granted query permissions.
        """
        table_instance = getattr(self, table)
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=[f"{table_instance.table_arn}/index/*"],
            )
        )

    def create_table(
        self,
        name: str,
        pk: str = "PK",
        pk_type: dynamo_db.AttributeType = dynamo_db.AttributeType.STRING,
        sk: Optional[str] = "SK",
        sk_type: Optional[dynamo_db.AttributeType] = dynamo_db.AttributeType.STRING,
        billing_mode: dynamo_db.BillingMode = dynamo_db.BillingMode.PAY_PER_REQUEST,
    ) -> dynamo_db.Table:
        """
        Create a DynamoDB table with the specified parameters.

        Args:
            name (str): The name of the table.
            pk (str, optional): The partition key for the table. Defaults to "PK".
            pk_type (dynamo_db.AttributeType, optional): The type of the partition key. Defaults to dynamo_db.AttributeType.STRING.
            sk (str, optional): The sort key for the table. Defaults to "SK".
            sk_type (dynamo_db.AttributeType, optional): The type of the sort key. Defaults to dynamo_db.AttributeType.STRING.
            billing_mode (dynamo_db.BillingMode, optional): The billing mode for the table. Defaults to dynamo_db.BillingMode.PAY_PER_REQUEST.

        Returns:
            dynamo_db.Table: The created DynamoDB table.
        """
        return dynamo_db.Table(
            self.scope,
            name,
            table_name=self.context.gen_id(name),
            partition_key=dynamo_db.Attribute(name=pk, type=pk_type),
            sort_key=dynamo_db.Attribute(name=sk, type=sk_type),
            billing_mode=billing_mode,
        )
