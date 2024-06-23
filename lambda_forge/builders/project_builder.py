import json

from lambda_forge.builders.file_service import FileService


class ProjectBuilder(FileService):
    @staticmethod
    def a_project(name, no_docs, minimal):
        return ProjectBuilder(name, no_docs, minimal)

    def __init__(self, name, no_docs, minimal):
        self.name = name
        self.no_docs = no_docs
        self.minimal = minimal

    def with_cdk(self, repo_owner, repo_name, account, region, bucket):
        cdk = {
            "app": "python3 app.py",
            "watch": {
                "include": ["**"],
                "exclude": [
                    "README.md",
                    "cdk*.json",
                    "requirements*.txt",
                    "source.bat",
                    "**/__init__.py",
                    "python/__pycache__",
                    "tests",
                ],
            },
            "context": {
                "@aws-cdk/aws-lambda:recognizeLayerVersion": True,
                "@aws-cdk/core:checkSecretUsage": True,
                "@aws-cdk/core:target-partitions": ["aws", "aws-cn"],
                "@aws-cdk-containers/ecs-service-extensions:enableDefaultLogDriver": True,
                "@aws-cdk/aws-ec2:uniqueImdsv2TemplateName": True,
                "@aws-cdk/aws-ecs:arnFormatIncludesClusterName": True,
                "@aws-cdk/aws-iam:minimizePolicies": True,
                "@aws-cdk/core:validateSnapshotRemovalPolicy": True,
                "@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName": True,
                "@aws-cdk/aws-s3:createDefaultLoggingPolicy": True,
                "@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption": True,
                "@aws-cdk/aws-apigateway:disableCloudWatchRole": True,
                "@aws-cdk/core:enablePartitionLiterals": True,
                "@aws-cdk/aws-events:eventsTargetQueueSameAccount": True,
                "@aws-cdk/aws-iam:standardizedServicePrincipals": True,
                "@aws-cdk/aws-ecs:disableExplicitDeploymentControllerForCircuitBreaker": True,
                "@aws-cdk/aws-iam:importedRoleStackSafeDefaultPolicyName": True,
                "@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy": True,
                "@aws-cdk/aws-route53-patters:useCertificate": True,
                "@aws-cdk/customresources:installLatestAwsSdkDefault": False,
                "region": region,
                "account": account,
                "name": self.name.title().replace("_", "-").replace(" ", "-"),
                "repo": {"owner": repo_owner, "name": repo_name},
                "bucket": bucket,
                "base_url": "",
            },
        }

        if self.minimal:
            cdk["context"]["resources"] = {"arns": {}}
        else:
            cdk["context"]["dev"] = {"arns": {}}
            cdk["context"]["staging"] = {"arns": {}}
            cdk["context"]["prod"] = {"arns": {}}
        
        self.cdk = json.dumps(cdk, indent=2)
        return self

    def build(self):
        self.copy_folders("lambda_forge", "scaffold", "")
        if self.minimal:
            self.copy_file("lambda_forge", "stacks/minimal/app.py", "")
            self.copy_file("lambda_forge", "stacks/minimal/prod_stack.py", "infra/stacks/prod_stack.py")

        else:
            if self.no_docs:
                self.copy_file("lambda_forge", "stacks/no_docs/app.py", "")
                self.copy_file("lambda_forge", "stacks/no_docs/prod_stack.py", "infra/stacks/prod_stack.py")
                self.copy_file("lambda_forge", "stacks/no_docs/dev_stack.py", "infra/stacks/dev_stack.py")
                self.copy_file("lambda_forge", "stacks/no_docs/staging_stack.py", "infra/stacks/staging_stack.py")
            else:
                self.copy_file("lambda_forge", "stacks/default/app.py", "")
                self.copy_file("lambda_forge", "stacks/default/prod_stack.py", "infra/stacks/prod_stack.py")
                self.copy_file("lambda_forge", "stacks/default/dev_stack.py", "infra/stacks/dev_stack.py")
                self.copy_file("lambda_forge", "stacks/default/staging_stack.py", "infra/stacks/staging_stack.py")

        self.make_file("", "cdk.json", self.cdk)
