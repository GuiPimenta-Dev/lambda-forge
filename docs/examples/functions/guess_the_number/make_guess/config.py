from infra.services import Services


class MakeGuessConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="MakeGuess",
            path="./functions/guess_the_number",
            description="Make a guess for a particular game",
            directory="make_guess",
            environment={"NUMBERS_TABLE_NAME": services.dynamodb.numbers_table.table_name},
        )

        services.api_gateway.create_endpoint("GET", "/games/{game_id}", function, public=True)

        services.dynamodb.numbers_table.grant_read_data(function)
