from infra.services import Services


class UpdatePostConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="UpdatePost",
            path="./functions/blog",
            description="Update a post",
            directory="update_post",
            environment={"POSTS_TABLE_NAME": services.dynamodb.posts_table.table_name},
        )

        services.api_gateway.create_endpoint("PUT", "/posts/{post_id}", function, authorizer="cognito")

        services.dynamodb.grant_write("posts_table", function)
        services.dynamodb.posts_table.grant_read_data(function)
