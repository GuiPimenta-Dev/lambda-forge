from infra.services import Services


class ListPostsConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="ListPosts",
            path="./functions/blog",
            description="List posts paginated",
            directory="list_posts",
            environment={"POSTS_TABLE_NAME": services.dynamodb.posts_table.table_name},
        )

        services.api_gateway.create_endpoint("GET", "/posts", function, authorizer="cognito")

        services.dynamodb.posts_table.grant_read_data(function)
