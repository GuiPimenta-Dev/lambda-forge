from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import Lambda


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = Lambda(scope, context)
