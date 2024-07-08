from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import Lambda
from infra.services.layers import Layers
from infra.services.sns import SNS


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = Lambda(scope, context)
        self.layers = Layers(scope)
        self.sns = SNS(scope, context)
