from aws_cdk import aws_iam as iam
from infra.services import Services


class GetChartConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="GetChart",
            path="./functions/chart",
            description="Rate interactions based on transcription and chat",
            directory="get_chart",
            environment={
                "TRANSCRIPTIONS_TABLE_NAME": services.dynamodb.transcriptions_table.table_name,
            },
        )

        services.api_gateway.create_endpoint("GET", "/chart", function, public=True)

        services.dynamodb.transcriptions_table.grant_read_data(function)

        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=[f"{services.dynamodb.transcriptions_table.table_arn}/index/*"],
            )
        )
