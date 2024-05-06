from lambda_forge.services import APIGateway, Lambda


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = Lambda(scope, context)
