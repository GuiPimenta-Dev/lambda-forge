from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import Lambda
from infra.services.dynamodb import DynamoDB
from infra.services.layers import Layers
from infra.services.parameter_store import ParameterStore
from infra.services.secrets_manager import SecretsManager


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = Lambda(scope, context)
        self.secrets_manager = SecretsManager(scope, context)
        self.layers = Layers(scope)
        self.parameter_store = ParameterStore(scope, context)
        self.dynamodb = DynamoDB(scope, context)
