from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import AWSLambda
from infra.services.sns import SNS


class Services:
    def __init__(self, scope, stage, arns, alarms, versioning) -> None:
        self.sns = SNS(scope)
        self.api_gateway = APIGateway(scope, stage)
        self.aws_lambda = AWSLambda(scope, stage, alarms, versioning, self.sns)
        