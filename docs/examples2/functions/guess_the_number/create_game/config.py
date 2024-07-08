from infra.services import Services


class CreateGameConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CreateGame",
            path="./functions/guess_the_number",
            description="Creates a new guess the number game",
            directory="create_game",
            environment={"NUMBERS_TABLE_NAME": services.dynamodb.numbers_table.table_name},
        )

        services.api_gateway.create_endpoint("POST", "/games", function, public=True)

        services.dynamodb.grant_write("numbers_table", function)
