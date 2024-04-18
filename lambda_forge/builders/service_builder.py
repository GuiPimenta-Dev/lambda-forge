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
        self.context = context

        # self.sns_topic = Topic.from_topic_arn(
        #     scope,
        #     id="SNSTopic",
        #     topic_arn=context.resources["arns"]["sns_topic_arn"],
        # )
        ...

    def create_trigger(self, topic, function, stages=None):
        if stages and self.context.stage not in stages:
            return

        sns_subscription = aws_lambda_event_sources.SnsEventSource(topic)
        function.add_event_source(sns_subscription)
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

        # self.dynamo = dynamo_db.Table.from_table_arn(
        #     scope,
        #     "Dynamo",
        #     context.resources["arns"]["dynamo_arn"],
        # )
        ...

    @staticmethod
    def add_query_permission(table, function):
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=[f"{table.table_arn}/index/*"],
            )
        )
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

        # self.secrets_manager = secrets_manager.Secret.from_secret_complete_arn(
        #     scope,
        #     id="SecretsManager",
        #     secret_complete_arn=context.resources["arns"]["secrets_manager_arn"],
        # )
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

        # self.cognito = cognito.UserPool.from_user_pool_arn(
        #     scope,
        #     "Cognito",
        #     user_pool_arn=context.resources["arns"]["cognito_arn"],
        # )
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

        # self.s3 = s3.Bucket.from_bucket_arn(
        #     scope,
        #     "S3",
        #     bucket_arn=context.resources["arns"]["s3_arn"],
        # )
        ...

    def create_trigger(self, bucket, function, stages=None):
        if stages and self.context.stage not in stages:
            return

        notifications = aws_s3_notifications.LambdaDestination(function)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notifications)

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

        # self.kms = kms.Key.from_key_arn(
        #     scope,
        #     "KMS",
        #     key_arn=context.resources["arns"]["kms_arn"],
        # )
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
        f = """from aws_cdk import aws_iam as iam
from aws_cdk.aws_lambda import CfnPermission
from b_aws_websocket_api.ws_api import WsApi
from b_aws_websocket_api.ws_deployment import WsDeployment
from b_aws_websocket_api.ws_lambda_integration import WsLambdaIntegration
from b_aws_websocket_api.ws_route import WsRoute
from b_aws_websocket_api.ws_stage import WsStage


class Websockets:
    def __init__(self, scope, context, name=None) -> None:
        self.scope = scope
        self.context = context
        self.name = name or context.name

        self.websocket = WsApi(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-WebSocket",
            name=f"{self.context.stage}-{self.name}-WebSocket",
            route_selection_expression="$request.body.action",
        )

        self.stage = WsStage(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-WSS-Stage",
            ws_api=self.websocket,
            stage_name=context.stage.lower(),
            auto_deploy=True,
        )

        self.deployment = WsDeployment(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-Deploy",
            ws_stage=self.stage,
        )

        self.deployment.node.add_dependency(self.stage)

    def create_route(self, route_key, function):
        route_name = route_key.replace("$", "")

        CfnPermission(
            scope=self.scope,
            id=f"{function}-{self.name}-{route_name}-Invoke",
            action="lambda:InvokeFunction",
            function_name=function.function_name,
            principal="apigateway.amazonaws.com",
        )

        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["execute-api:ManageConnections"],
                resources=["*"],
            )
        )

        integration = WsLambdaIntegration(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-Integration-{route_name}",
            integration_name=f"{self.context.stage}-{self.name}-Integration-{route_name}",
            ws_api=self.websocket,
            function=function,
        )

        route = WsRoute(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-Route-{route_name}",
            ws_api=self.websocket,
            route_key=route_key,
            authorization_type="NONE",
            route_response_selection_expression="$default",
            target=f"integrations/{integration.ref}",
        )

        self.deployment.node.add_dependency(route)
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

        # self.sqs = sqs.Queue.from_queue_arn(
        #     scope,
        #     "SQS",
        #     queue_arn=context.resources["arns"]["sqs_arn"],
        # )
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
        self.scope = scope
        self.context = context
        
    def create_rule(self, name, expression, target, stages=None):
        if stages is not None and self.context.stage not in stages:
            return
            
        events.Rule(
            self.scope,
            name,
            schedule=events.Schedule.expression(expression),
            targets=[targets.LambdaFunction(handler=target)],
        )
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
