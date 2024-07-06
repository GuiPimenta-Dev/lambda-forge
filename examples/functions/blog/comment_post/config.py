from infra.services import Services


class CommentPostConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CommentPost", path="./functions/blog", description="Comment on a blog post", directory="comment_post"
        )

        services.api_gateway.create_endpoint("POST", "/comments/{post_id}", function, public=True)


