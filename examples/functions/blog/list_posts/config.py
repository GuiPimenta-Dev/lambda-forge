from infra.services import Services


class ListPostsConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="ListPosts", path="./functions/blog", description="List posts paginated", directory="list_posts"
        )

        services.api_gateway.create_endpoint("GET", "/posts", function, public=True)
