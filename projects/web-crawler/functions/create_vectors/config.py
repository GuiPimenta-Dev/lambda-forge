from infra.services import Services

class CreateVectorsConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CreateVectors",
            path="./functions/create_vectors",
            description="vectorize the scraped data",
            layers=[services.layers.sm_utils_layer],
        )

        services.api_gateway.create_endpoint("POST", "/create_vectors", function, public=True)

            