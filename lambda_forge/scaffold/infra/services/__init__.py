from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import AWSLambda
from infra.services.layers import Layers


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = AWSLambda(scope, context)
        self.layers = Layers(scope)
