from lambda_forge.builders.file_service import FileService


class ServiceBuilder(FileService):
    @staticmethod
    def a_service():
        return ServiceBuilder()

    def __init__(self) -> None:
        self.services = self.read_lines("infra/services/__init__.py")

    def with_sns(self):
        f = """from aws_cdk import aws_sns as sns
from aws_cdk import aws_lambda_event_sources
from lambda_forge.trackers import trigger, invoke


class SNS:
    def __init__(self, scope, resources) -> None:
    
        # self.sns_topic = sns.Topic.from_topic_arn(
        #     scope,
        #     id="SNSTopic",
        #     topic_arn=resources["arns"]["sns_topic_arn"],
        # )
        ...

    @trigger(service="sns", trigger="topic", function="function")
    def add_event_source(self, topic, function):
        topic = getattr(self, topic)
        sns_subscription = aws_lambda_event_sources.SnsEventSource(topic)
        function.add_event_source(sns_subscription)
    
    @invoke(service="sns", resource="topic", function="function")
    def grant_publish(self, topic, function):
        topic = getattr(self, topic)
        topic.grant_publish(function)
"""
        file_exists = self.file_exists("infra/services/sns.py")
        if not file_exists:
            self.make_file("infra/services", "sns.py", f)
            self.update_services(
                "from infra.services.sns import SNS",
                "self.sns = SNS(scope, context.resources)",
            )

        return self

    def with_layers(self):
        f = """from aws_cdk import aws_lambda as _lambda
from lambda_forge import Path


class Layers:
    def __init__(self, scope) -> None:

        # self.layer = _lambda.LayerVersion.from_layer_version_arn(
        #     scope,
        #     id="Layer",
        #     layer_version_arn="",
        # )
        ...
"""
        file_exists = self.file_exists("infra/services/layers.py")
        if not file_exists:
            self.make_file("infra/services", "layers.py", f)
            self.update_services("from infra.services.layers import Layers", "self.layers = Layers(scope)")

        return self

    def with_dynamodb(self):
        f = """from aws_cdk import aws_dynamodb as dynamodb
from lambda_forge.trackers import invoke


class DynamoDB:
    def __init__(self, scope, resources: dict) -> None:

        # self.dynamo = dynamo_db.Table.from_table_arn(
        #     scope,
        #     "Dynamo",
        #     resources["arns"]["dynamo_arn"],
        # )
        ...
        
    @invoke(service="dynamodb", resource="table", function="function")
    def grant_write_data(self, table, function):
        table = getattr(self, table)
        table.grant_write_data(function)
"""
        file_exists = self.file_exists("infra/services/dynamodb.py")
        if not file_exists:
            self.make_file("infra/services", "dynamodb.py", f)
            self.update_services(
                "from infra.services.dynamodb import DynamoDB",
                "self.dynamodb = DynamoDB(scope, context.resources)",
            )

        return self

    def with_secrets_manager(self):
        f = """from aws_cdk import aws_secretsmanager as secrets_manager

        
class SecretsManager:
    def __init__(self, scope, resources) -> None:

        # self.secrets_manager = secrets_manager.Secret.from_secret_complete_arn(
        #     scope,
        #     id="SecretsManager",
        #     secret_complete_arn=resources["arns"]["secrets_manager_arn"],
        # )
        pass
"""
        file_exists = self.file_exists("infra/services/secrets_manager.py")
        if not file_exists:
            self.make_file("infra/services", "secrets_manager.py", f)
            self.update_services(
                "from infra.services.secrets_manager import SecretsManager",
                "self.secrets_manager = SecretsManager(scope, context.resources)",
            )

        return self

    def with_cognito(self):
        f = """from aws_cdk import aws_cognito as cognito


class Cognito:
    def __init__(self, scope, resources) -> None:

        # self.cognito = cognito.UserPool.from_user_pool_arn(
        #     scope,
        #     "Cognito",
        #     user_pool_arn=resources["arns"]["cognito_arn"],
        # )
        pass
"""
        file_exists = self.file_exists("infra/services/cognito.py")
        if not file_exists:
            self.make_file("infra/services", "cognito.py", f)
            self.update_services(
                "from infra.services.cognito import Cognito",
                "self.cognito = Cognito(scope, context.resources)",
            )

        return self

    def with_s3(self):
        f = """from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications
from lambda_forge.trackers import trigger


class S3:
    def __init__(self, scope, resources) -> None:
        
        # self.s3 = s3.Bucket.from_bucket_arn(
        #     scope,
        #     "S3",
        #     bucket_arn=resources["arns"]["s3_arn"],
        # )
        ...

    @trigger(service="s3", trigger="bucket", function="function")
    def add_event_notification(self, bucket, function):
        bucket = getattr(self, bucket)
        notifications = aws_s3_notifications.LambdaDestination(function)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notifications)
        bucket.grant_read(function)


    @invoke(service="s3", resource="bucket", function="function")
    def grant_write(self, bucket, function):
        bucket = getattr(self, bucket)
        bucket.grant_write(function)
"""
        file_exists = self.file_exists("infra/services/s3.py")
        if not file_exists:
            self.make_file("infra/services", "s3.py", f)
            self.update_services("from infra.services.s3 import S3", "self.s3 = S3(scope, context.resources)")

        return self

    def with_kms(self):
        f = """from aws_cdk import aws_kms as kms


class KMS:
    def __init__(self, scope, resources) -> None:

        # self.kms = kms.Key.from_key_arn(
        #     scope,
        #     "KMS",
        #     key_arn=resources["arns"]["kms_arn"],
        # )
        pass
    """
        file_exists = self.file_exists("infra/services/kms.py")
        if not file_exists:
            self.make_file("infra/services", "kms.py", f)
            self.update_services(
                "from infra.services.kms import KMS",
                "self.kms = KMS(scope, context.resources)",
            )

        return self

    def with_sqs(self):
        f = """from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_lambda_event_sources
from lambda_forge.trackers import trigger, invoke


class SQS:
    def __init__(self, scope, resources) -> None:
        
        # self.sqs = sqs.Queue.from_queue_arn(
        #     scope,
        #     "SQS",
        #     queue_arn=resources["arns"]["sqs_arn"],
        # )
        ...
    
    @trigger(service="sqs", trigger="queue", function="function")
    def add_event_source(self, queue, function):
        queue = getattr(self, queue)
        event_source = aws_lambda_event_sources.SqsEventSource(queue)
        function.add_event_source(event_source)
        queue.grant_consume_messages(function)


    @invoke(service="sqs", resource="queue", function="function")
    def grant_send_messages(self, queue, function):
        queue = getattr(self, queue)
        queue.grant_send_messages(function)
    """
        file_exists = self.file_exists("infra/services/sqs.py")
        if not file_exists:
            self.make_file("infra/services", "sqs.py", f)
            self.update_services(
                "from infra.services.sqs import SQS",
                "self.sqs = SQS(scope, context.resources)",
            )

        return self

    def with_event_bridge(self):
        f = """
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as targets
from lambda_forge.trackers import trigger


class EventBridge:
    def __init__(self, scope) -> None:
        self.scope = scope
        
    @trigger(service="event_bridge", trigger="rule_name", function="function")
    def schedule(self, rule_name, expression, function):
        events.Rule(
            self.scope,
            rule_name,
            schedule=events.Schedule.expression(expression),
            targets=[targets.LambdaFunction(handler=function)],
        )
"""
        file_exists = self.file_exists("infra/services/event_bridge.py")
        if not file_exists:
            self.make_file("infra/services", "event_bridge.py", f)
            self.update_services(
                "from infra.services.event_bridge import EventBridge",
                "self.event_bridge = EventBridge(scope)",
            )

        return self

    def update_services(self, import_statement, instance_statement):
        self.services.insert(0, f"{import_statement}\n")
        self.services.append(f"        {instance_statement}\n")

    def build(self):
        self.write_lines("infra/services/__init__.py", self.services)

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
