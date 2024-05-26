from aws_cdk import aws_dynamodb as dynamodb

from lambda_forge.services import NoSQL


class DynamoDB(NoSQL):
    def __init__(self, scope, context) -> None:
        super().__init__(scope=scope, context=context)

        # self.dynamo = dynamodb.Table.from_table_arn(
        #     scope,
        #     "Dynamo",
        #     context.resources["arns"]["dynamo_arn"],
        # )
        ...
