from infra.services import Services

class HelloWorldConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="HelloWorld",
            path="./functions/somewhere",
            description="A simple hello word",
            directory="hello_world"
        )

        services.api_gateway.create_endpoint("GET", "/somewhere", function, public=True)

            