from functions.guess_the_number.make_guess.config import MakeGuessConfig
from functions.guess_the_number.create_game.config import CreateGameConfig
from docs.config import DocsConfig
from aws_cdk import Stack
from constructs import Construct
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Docs
        DocsConfig(self.services)

        # GuessTheNumber
        MakeGuessConfig(self.services)
        CreateGameConfig(self.services)
