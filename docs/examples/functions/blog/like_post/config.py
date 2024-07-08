from infra.services import Services


class LikePostConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="LikePost",
            path="./functions/blog",
            description="Like a post",
            directory="like_post",
            environment={"POSTS_TABLE_NAME": services.dynamodb.posts_table.table_name},
        )

        services.api_gateway.create_endpoint("POST", "/posts/{post_id}/like", function, authorizer="cognito")

        services.dynamodb.grant_write("posts_table", function)
        services.dynamodb.posts_table.grant_read_data(function)
