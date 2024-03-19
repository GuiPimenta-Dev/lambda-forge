from infra.services import Services

class HelloWorldConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="HelloWorld",
            path="./functions/hello_world",
            description="A simple hello word",
            
        )

        services.api_gateway.create_endpoint("GET", "/hello_world", function, public=True)

            