from lambda_forge.file_service import FileService


class ServiceBuilder(FileService):
    @staticmethod
    def a_service():
        return ServiceBuilder()

    def __init__(self) -> None:
        self.services = self.read_lines("infra/services/__init__.py")

    def with_sns(self):
        f = """from aws_cdk.aws_sns import Topic


class SNS:
    def __init__(self, scope, arns) -> None:

        self.sns_topic = Topic.from_topic_arn(
            scope,
            id="SNSTopic",
            topic_arn=arns["sns_topic_arn"],
        )
"""
        self.make_file("infra/services", "sns.py", f)
        self.update_services(
            "from infra.services.sns import SNS", "self.sns = SNS(scope, arns)"
        )

        return self

    def with_layers(self):
        f = """from aws_cdk import aws_lambda as _lambda


class Layers:
    def __init__(self, scope) -> None:

        self.layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="Layer",
            layer_version_arn="",
        )
"""
        self.make_file("infra/services", "layers.py", f)
        self.update_services(
            "from infra.services.layers import Layers", "self.layers = Layers(scope)"
        )

        return self

    def with_dynamodb(self):
        f = """from aws_cdk import aws_dynamodb as dynamo_db
from aws_cdk import aws_iam as iam
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks


class DynamoDB:
    def __init__(self, scope, arns: dict) -> None:

        self.dynamo = dynamo_db.Table.from_table_arn(
            scope,
            "Dynamo",
            arns["dynamo_arn"],
        )

    @staticmethod
    def add_query_permission(function, table):
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=[f"{table.table_arn}/index/*"],
            )
        )
"""
        self.make_file("infra/services", "dynamo_db.py", f)
        self.update_services(
            "from infra.services.dynamo_db import DynamoDB",
            "self.dynamo_db = DynamoDB(scope, arns)",
        )

        return self

    def with_secrets_manager(self):
        f = """from aws_cdk import aws_secretsmanager as secrets_manager

        
class SecretsManager:
    def __init__(self, scope, arns) -> None:

        self.secrets_manager = secrets_manager.Secret.from_secret_complete_arn(
            scope,
            id="SecretsManager",
            secret_complete_arn=arns["secrets_manager_arn"],
        )
"""
        self.make_file("infra/services", "secrets_manager.py", f)
        self.update_services(
            "from infra.services.secrets_manager import SecretsManager",
            "self.secrets_manager = SecretsManager(scope, arns)",
        )

        return self

    def with_cognito(self):
        f = """from aws_cdk import aws_cognito as cognito


class Cognito:
    def __init__(self, scope, arns) -> None:

        self.cognito = cognito.UserPool.from_user_pool_arn(
            scope,
            "Cognito",
            user_pool_arn=arns["cognito_arn"],
        )
"""
        self.make_file("infra/services", "cognito.py", f)
        self.update_services(
            "from infra.services.cognito import Cognito",
            "self.cognito = Cognito(scope, arns)",
        )

        return self

    def with_s3(self):
        f = """from aws_cdk import aws_s3 as s3


class S3:
    def __init__(self, scope, arns) -> None:

        self.s3 = s3.Bucket.from_bucket_arn(
            scope,
            "S3",
            bucket_arn=arns["s3_arn"],
        )
"""

        self.make_file("infra/services", "s3.py", f)
        self.update_services(
            "from infra.services.s3 import S3", "self.s3 = S3(scope, arns)"
        )

        return self

    def with_kms(self):
        f = """from aws_cdk import aws_kms as kms


class KMS:
    def __init__(self, scope, arns) -> None:

        self.kms = kms.Key.from_key_arn(
            scope,
            "KMS",
            key_arn=arns["kms_arn"],
        )
    """
        self.make_file("infra/services", "kms.py", f)
        self.update_services(
            "from infra.services.kms import KMS", "self.kms = KMS(scope, arns)"
        )

        return self

    def with_sqs(self):
        f = """from aws_cdk import aws_sqs as sqs


class SQS:
    def __init__(self, scope, arns) -> None:

        self.sqs = sqs.Queue.from_queue_arn(
            scope,
            "SQS",
            queue_arn=arns["sqs_arn"],
        )
    """
        self.make_file("infra/services", "sqs.py", f)
        self.update_services(
            "from infra.services.sqs import SQS", "self.sqs = SQS(scope, arns)"
        )

        return self

    def with_state_machine(self):
        f = """from aws_cdk import aws_stepfunctions as state_machine


class StateMachine:
    def __init__(self, scope, arns: dict) -> None:
        self.state_machine = state_machine.StateMachine.from_state_machine_arn(
            scope,
            id="StateMachine",
            state_machine_arn=arns["state_machine_arn"],
        )

    """
        self.make_file("infra/services", "state_machine.py", f)
        self.update_services(
            "from infra.services.state_machine import StateMachine",
            "self.state_machine = StateMachine(scope, arns)",
        )

        return self

    def with_event_bridge(self):
        f = """
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as targets


class EventBridge:
    def __init__(self, scope, arns, stage) -> None:
        self.scope = scope
        self.stage = stage

        self.event_bridge = events.EventBus.from_event_bus_arn(
            scope,
            id="EventBridge",
            event_bus_arn=arns["event_bridge_arn"],
        )

    def create_rule(self, name, expression, target, only_prod=False):
        if only_prod and self.stage != "Prod":
            return
        events.Rule(
            self.scope,
            name,
            schedule=events.Schedule.expression(expression),
            targets=[targets.LambdaFunction(handler=target)],
        )
"""
        self.make_file("infra/services", "event_bridge.py", f)
        self.update_services(
            "from infra.services.event_bridge import EventBridge",
            "self.event_bridge = EventBridge(scope, arns, stage)",
        )

        return self

    def update_services(self, import_statement, instance_statement):
        self.services.insert(0, f"{import_statement}\n")
        self.services.append(f"        {instance_statement}\n")

    def build(self):
        self.write_lines("infra/services/__init__.py", self.services)
