from infra.services import Services


class CommentPostConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CommentPost",
            path="./functions/blog",
            description="Comment on a blog post",
            directory="comment_post",
            environment={"POSTS_TABLE_NAME": services.dynamodb.posts_table.table_name},
        )

        services.api_gateway.create_endpoint(
            "POST", "/posts/{post_id}/comments", function, authorizer="sso"
        )

        services.dynamodb.grant_write("posts_table", function)
        services.dynamodb.posts_table.grant_read_data(function)
