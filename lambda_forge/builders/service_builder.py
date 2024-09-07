from lambda_forge.builders.file_service import FileService


class ServiceBuilder(FileService):
    @staticmethod
    def a_service():
        return ServiceBuilder()

    def __init__(self) -> None:
        self.services = self.read_lines("infra/services/__init__.py")

    def with_sns(self):
        file_exists = self.file_exists("infra/services/sns.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge", "builders/services/sns.py", "infra/services/sns.py"
            )
            self.update_services(
                "from infra.services.sns import SNS",
                "self.sns = SNS(scope, context)",
            )

        return self

    def with_layers(self):

        file_exists = self.file_exists("infra/services/layers.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge",
                "builders/services/layers.py",
                "infra/services/layers.py",
            )
            self.update_services(
                "from infra.services.layers import Layers",
                "self.layers = Layers(scope)",
            )

        return self

    def with_dynamodb(self):
        file_exists = self.file_exists("infra/services/dynamodb.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge",
                "builders/services/dynamodb.py",
                "infra/services/dynamodb.py",
            )
            self.update_services(
                "from infra.services.dynamodb import DynamoDB",
                "self.dynamodb = DynamoDB(scope, context)",
            )

        return self

    def with_secrets_manager(self):
        file_exists = self.file_exists("infra/services/secrets_manager.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge",
                "builders/services/secrets_manager.py",
                "infra/services/secrets_manager.py",
            )
            self.update_services(
                "from infra.services.secrets_manager import SecretsManager",
                "self.secrets_manager = SecretsManager(scope, context)",
            )

        return self

    def with_cognito(self):

        file_exists = self.file_exists("infra/services/cognito.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge",
                "builders/services/cognito.py",
                "infra/services/cognito.py",
            )
            self.update_services(
                "from infra.services.cognito import Cognito",
                "self.cognito = Cognito(scope, context)",
            )

        return self

    def with_s3(self):
        file_exists = self.file_exists("infra/services/s3.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge", "builders/services/s3.py", "infra/services/s3.py"
            )
            self.update_services(
                "from infra.services.s3 import S3", "self.s3 = S3(scope, context)"
            )

        return self

    def with_kms(self):
        file_exists = self.file_exists("infra/services/kms.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge", "builders/services/kms.py", "infra/services/kms.py"
            )
            self.update_services(
                "from infra.services.kms import KMS",
                "self.kms = KMS(scope, context)",
            )

        return self

    def with_sqs(self):
        file_exists = self.file_exists("infra/services/sqs.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge", "builders/services/sqs.py", "infra/services/sqs.py"
            )
            self.update_services(
                "from infra.services.sqs import SQS",
                "self.sqs = SQS(scope, context)",
            )

        return self

    def with_event_bridge(self):
        file_exists = self.file_exists("infra/services/event_bridge.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge",
                "builders/services/event_bridge.py",
                "infra/services/event_bridge.py",
            )
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
        file_exists = self.file_exists("infra/services/websockets.py")
        if not file_exists:
            self.copy_file(
                "lambda_forge",
                "builders/services/websockets.py",
                "infra/services/websockets.py",
            )
            self.update_services(
                "from infra.services.websockets import Websockets",
                "self.websockets = Websockets(scope, context)",
            )

        return self
