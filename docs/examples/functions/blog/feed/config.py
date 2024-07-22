from infra.services import Services


class FeedConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Feed",
            path="./functions/blog",
            description="Get feed of posts",
            directory="feed",
            environment={"POSTS_TABLE_NAME": services.dynamodb.posts_table.table_name},
        )

        services.api_gateway.create_endpoint("GET", "/feed", function, public=True)

        services.dynamodb.posts_table.grant_read_data(function)
