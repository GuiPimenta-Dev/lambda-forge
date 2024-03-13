from aws_cdk import aws_dynamodb as dynamo_db
from aws_cdk import aws_iam as iam


class DynamoDB:
    def __init__(self, scope, arns: dict) -> None:

        self.control_table = dynamo_db.Table.from_table_arn(
            scope,
            "ControlTable",
            arns["control_table"],
        )

    @staticmethod
    def add_query_permissions(function, table):
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=[f"{table.table_arn}/index/*"],
            )
        )
