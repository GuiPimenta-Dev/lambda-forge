from infra.services import Services


class DeletePostConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="DeletePost",
            path="./functions/blog",
            description="Delete a post",
            directory="delete_post",
            environment={"POSTS_TABLE_NAME": services.dynamodb.posts_table.table_name},
        )

        services.api_gateway.create_endpoint("DELETE", "/posts/{post_id}", function, authorizer="sso")

        services.dynamodb.grant_write("posts_table", function)
        services.dynamodb.posts_table.grant_read_data(function)
