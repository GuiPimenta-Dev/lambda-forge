from aws_cdk import aws_iam as iam

from infra.services import Services


class CreateVectorsConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CreateVectors",
            path="./functions/rag",
            directory="create_vectors",
            description="vectorize the scraped data",
            layers=[
                services.layers.sm_utils_layer,
                services.layers.langchain_all_layer,
                services.layers.pinecone_client_layer,
                services.layers.tiktoken_layer,
                services.layers.pandas_layer,
            ],
            environment={
                "VISITED_URLS_TABLE_NAME": services.dynamodb.visited_urls_table.table_name,
            },
        )

        services.api_gateway.create_endpoint("POST", "/vectors", function)
        services.dynamodb.visited_urls_table.grant_read_data(function)
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=[f"{services.dynamodb.visited_urls_table.table_arn}/index/*"],
            )
        )

        services.secrets_manager.openai_api_secret.grant_read(function)
        services.secrets_manager.pinecone_api_secret.grant_read(function)
