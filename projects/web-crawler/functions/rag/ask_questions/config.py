from infra.services import Services


class AskQuestionsConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="AskQuestionsToLLM",
            path="./functions/rag",
            directory="ask_questions",
            description="ask for llm",
            memory_size=10240,
            layers=[
                services.layers.langchain_all_layer,
                services.layers.pinecone_client_layer,
                services.layers.tiktoken_layer,
            ],
            environment={
                "PINECONE_INDEX_NAME": "lambda-forge-telegram",
            },
        )

        services.api_gateway.create_endpoint("GET", "/question", function)

        services.secrets_manager.openai_api_secret.grant_read(function)
        services.secrets_manager.pinecone_api_secret.grant_read(function)
