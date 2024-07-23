from infra.services.layers import Layers
from infra.services.secrets_manager import SecretsManager
from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import Lambda


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = Lambda(scope, context)
        self.secrets_manager = SecretsManager(scope, context)
        self.layers = Layers(scope)
