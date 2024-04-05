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
    def __init__(self, scope, resources) -> None:

        # self.sns_topic = Topic.from_topic_arn(
        #     scope,
        #     id="SNSTopic",
        #     topic_arn=resources["arns"]["sns_topic_arn"],
        # )
        pass

    def create_trigger(self, topic, function, stages=None):
        if stages and self.stage not in stages:
            return

        sns_subscription = aws_lambda_event_sources.SnsEventSource(topic)
        function.add_event_source(sns_subscription)
"""
        file_exists = self.file_exists("infra/services/sns.py")
        if not file_exists:
            self.make_file("infra/services", "sns.py", f)
            self.update_services(
                "from infra.services.sns import SNS",
                "self.sns = SNS(scope, context.resources, context.stage)",
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
        pass
"""     
        file_exists = self.file_exists("infra/services/layers.py")
        if not file_exists:
            self.make_file("infra/services", "layers.py", f)
            self.update_services(
                "from infra.services.layers import Layers", "self.layers = Layers(scope)"
            )

        return self

    def with_dynamodb(self):
        f = """from aws_cdk import aws_dynamodb as dynamo_db
from aws_cdk import aws_iam as iam


class DynamoDB:
    def __init__(self, scope, resources: dict) -> None:

        # self.dynamo = dynamo_db.Table.from_table_arn(
        #     scope,
        #     "Dynamo",
        #     resources["arns"]["dynamo_arn"],
        # )
        pass

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
                "self.dynamo_db = DynamoDB(scope, context.resources)",
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


class S3:
    def __init__(self, scope, resources) -> None:

        # self.s3 = s3.Bucket.from_bucket_arn(
        #     scope,
        #     "S3",
        #     bucket_arn=resources["arns"]["s3_arn"],
        # )
        pass
"""
        file_exists = self.file_exists("infra/services/s3.py")
        if not file_exists:
            self.make_file("infra/services", "s3.py", f)
            self.update_services(
                "from infra.services.s3 import S3", "self.s3 = S3(scope, context.resources)"
            )

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


class SQS:
    def __init__(self, scope, resources) -> None:

        # self.sqs = sqs.Queue.from_queue_arn(
        #     scope,
        #     "SQS",
        #     queue_arn=resources["arns"]["sqs_arn"],
        # )
        pass
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


class EventBridge:
    def __init__(self, scope, resources, stage) -> None:
        self.scope = scope
        self.stage = stage
        
    def create_rule(self, name, expression, target, stages=None):
        if stages is not None and self.stage not in stages:
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
                "self.event_bridge = EventBridge(scope, context.resources, context.stage)",
            )

        return self

    def update_services(self, import_statement, instance_statement):
        self.services.insert(0, f"{import_statement}\n")
        self.services.append(f"        {instance_statement}\n")

    def build(self):
        self.write_lines("infra/services/__init__.py", self.services)
