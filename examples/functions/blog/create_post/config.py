from infra.services import Services


class CreatePostConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CreatePost", path="./functions/blog", description="Create a new post", directory="create_post"
        )

        services.api_gateway.create_endpoint("POST", "/posts", function, public=True)
