from infra.services import Services


class CreatePostConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CreatePost",
            path="./functions/blog",
            description="Create a new post",
            directory="create_post",
            environment={"POSTS_TABLE_NAME": services.dynamodb.posts_table.table_name},
        )

        services.api_gateway.create_endpoint("POST", "/posts", function, authorizer="sso")

        services.dynamodb.grant_write("posts_table", function)
