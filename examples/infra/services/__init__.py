from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import Lambda
from infra.services.dynamodb import DynamoDB
from infra.services.kms import KMS
from infra.services.layers import Layers
from infra.services.s3 import S3
from infra.services.secrets_manager import SecretsManager
from infra.services.websockets import Websockets


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = Lambda(scope, context)
        self.dynamodb = DynamoDB(scope, context)
        self.s3 = S3(scope, context)
        self.secrets_manager = SecretsManager(scope, context)
        self.layers = Layers(scope)
        self.kms = KMS(scope, context)
        self.websockets = Websockets(scope, context)
