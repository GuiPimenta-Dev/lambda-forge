from infra.services.secrets_manager import SecretsManager
from infra.services.s3 import S3
from infra.services.dynamodb import DynamoDB
from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import Lambda
from infra.services.layers import Layers

class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = Lambda(scope, context)
        self.dynamodb = DynamoDB(scope, context)
        self.s3 = S3(scope, context)
        self.secrets_manager = SecretsManager(scope, context)
        self.layers = Layers(scope)
