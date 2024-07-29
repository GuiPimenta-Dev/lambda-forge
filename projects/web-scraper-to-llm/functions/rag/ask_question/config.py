from infra.services import Services

class AskQuestionConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="AskQuestion",
            path="./functions/rag",
            description="anything",
            directory="ask_question",
            memory_size=10240,
            layers=[
                services.layers.sm_utils_layer,
                services.layers.langchain_all_layer,
            ],
        )

        services.api_gateway.create_endpoint("GET", "/ask", function)

        services.secrets_manager.openai_api_secret.grant_read(function)
