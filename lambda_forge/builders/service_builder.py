from lambda_forge.builders.file_service import FileService


class ServiceBuilder(FileService):
    @staticmethod
    def a_service():
        return ServiceBuilder()

    def __init__(self) -> None:
        self.services = self.read_lines("infra/services/__init__.py")

    def with_sns(self):
        f = """from aws_cdk.aws_sns import Topic
from aws_cdk import aws_lambda_event_sources


class SNS:
    def __init__(self, scope, context) -> None:
        ...
"""
        file_exists = self.file_exists("infra/services/sns.py")
        if not file_exists:
            self.make_file("infra/services", "sns.py", f)
            self.update_services(
                "from infra.services.sns import SNS",
                "self.sns = SNS(scope, context)",
            )

        return self

    def with_layers(self):
        f = """from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:
        ...
"""
        file_exists = self.file_exists("infra/services/layers.py")
        if not file_exists:
            self.make_file("infra/services", "layers.py", f)
            self.update_services(
                "from infra.services.layers import Layers",
                "self.layers = Layers(scope)",
            )

        return self

    def with_dynamodb(self):
        f = """from aws_cdk import aws_dynamodb as dynamo_db
from aws_cdk import aws_iam as iam


class DynamoDB:
    def __init__(self, scope, context) -> None:
        ...

"""
        file_exists = self.file_exists("infra/services/dynamo_db.py")
        if not file_exists:
            self.make_file("infra/services", "dynamo_db.py", f)
            self.update_services(
                "from infra.services.dynamo_db import DynamoDB",
                "self.dynamo_db = DynamoDB(scope, context)",
            )

        return self

    def with_secrets_manager(self):
        f = """from aws_cdk import aws_secretsmanager as secrets_manager

        
class SecretsManager:
    def __init__(self, scope, context) -> None:
        ...
"""
        file_exists = self.file_exists("infra/services/secrets_manager.py")
        if not file_exists:
            self.make_file("infra/services", "secrets_manager.py", f)
            self.update_services(
                "from infra.services.secrets_manager import SecretsManager",
                "self.secrets_manager = SecretsManager(scope, context)",
            )

        return self

    def with_cognito(self):
        f = """from aws_cdk import aws_cognito as cognito


class Cognito:
    def __init__(self, scope, context) -> None:
        ...
"""
        file_exists = self.file_exists("infra/services/cognito.py")
        if not file_exists:
            self.make_file("infra/services", "cognito.py", f)
            self.update_services(
                "from infra.services.cognito import Cognito",
                "self.cognito = Cognito(scope, context)",
            )

        return self

    def with_s3(self):
        f = """from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications


class S3:
    def __init__(self, scope, context) -> None:
        ...
"""
        file_exists = self.file_exists("infra/services/s3.py")
        if not file_exists:
            self.make_file("infra/services", "s3.py", f)
            self.update_services("from infra.services.s3 import S3", "self.s3 = S3(scope, context)")

        return self

    def with_kms(self):
        f = """from aws_cdk import aws_kms as kms


class KMS:
    def __init__(self, scope, context) -> None:
        ...
    """
        file_exists = self.file_exists("infra/services/kms.py")
        if not file_exists:
            self.make_file("infra/services", "kms.py", f)
            self.update_services(
                "from infra.services.kms import KMS",
                "self.kms = KMS(scope, context)",
            )

        return self

    def with_websockets(self):
        f = """from b_aws_websocket_api.ws_api import WsApi
from lambda_forge.websockets import WSS


class Websockets:
    def __init__(self, scope, context, name=None) -> None:
        
        wss = WsApi(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-WebSocket",
            name=f"{self.context.stage}-{self.name}-WebSocket",
            route_selection_expression="$request.body.action",
        )
        
        self.wss = WSS(scope=scope, context=context, name=context.name, wss=wss)


    def create_route(self, route_key, function):
        self.wss.create_route(route_key=route_key, function=function)
"""
        file_exists = self.file_exists("infra/services/websockets.py")
        if not file_exists:
            self.make_file("infra/services", "websockets.py", f)
            self.update_services(
                "from infra.services.websockets import Websockets",
                "self.websockets = Websockets(scope, context)",
            )

        return self

    def with_sqs(self):
        f = """from aws_cdk import aws_sqs as sqs


class SQS:
    def __init__(self, scope, context) -> None:
        ...
    """
        file_exists = self.file_exists("infra/services/sqs.py")
        if not file_exists:
            self.make_file("infra/services", "sqs.py", f)
            self.update_services(
                "from infra.services.sqs import SQS",
                "self.sqs = SQS(scope, context)",
            )

        return self

    def with_event_bridge(self):
        f = """
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as targets


class EventBridge:
    def __init__(self, scope, context) -> None:
        ...
"""
        file_exists = self.file_exists("infra/services/event_bridge.py")
        if not file_exists:
            self.make_file("infra/services", "event_bridge.py", f)
            self.update_services(
                "from infra.services.event_bridge import EventBridge",
                "self.event_bridge = EventBridge(scope, context, context.stage)",
            )

        return self

    def update_services(self, import_statement, instance_statement):
        self.services.insert(0, f"{import_statement}\n")
        self.services.append(f"        {instance_statement}\n")

    def build(self):
        self.write_lines("infra/services/__init__.py", self.services)
