from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_iam as iam
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource


class CodeBuildStep:
    def __init__(self, scope, stage, source: CodePipelineSource):
        self.scope = scope
        self.stage = stage
        self.source = source

    def run_unit_tests(self):
        report_group = codebuild.ReportGroup(
            self.scope,
            "UnitReportGroup",
        )

        return pipelines.CodeBuildStep(
            "Unit Test",
            input=self.source,
            install_commands=[
                "pip install -r requirements.txt",
            ],
            commands=[
                'pytest --junitxml=pytest-report/test-results.xml -k "unit.py"',
            ],
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(
                {
                    "reports": {
                        report_group.report_group_arn: {
                            "files": "test-results.xml",
                            "base-directory": "pytest-report",
                            "file-format": "JUNITXML",
                        }
                    }
                }
            ),
            role_policy_statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "codebuild:CreateReportGroup",
                        "codebuild:CreateReport",
                        "codebuild:UpdateReport",
                        "codebuild:BatchPutTestCases",
                        "codebuild:BatchPutCodeCoverages",
                    ],
                    resources=[report_group.report_group_arn],
                )
            ],
        )

    def run_coverage(self):
        report_group = codebuild.ReportGroup(
            self.scope,
            "CoverageGroup",
            type=codebuild.ReportGroupType.CODE_COVERAGE,
        )
        coverage = self.scope.node.try_get_context("coverage") or 80
        return pipelines.CodeBuildStep(
            "Coverage",
            input=self.source,
            install_commands=[
                "pip install -r requirements.txt",
            ],
            commands=[
                'coverage run -m pytest -k "unit.py"',
                f"coverage xml --fail-under={coverage}",
                "touch coverage.xml",
            ],
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(
                {
                    "reports": {
                        report_group.report_group_arn: {
                            "files": "coverage.xml",
                            "base-directory": ".",
                            "file-format": "COBERTURAXML",
                        }
                    }
                }
            ),
            role_policy_statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "codebuild:CreateReportGroup",
                        "codebuild:CreateReport",
                        "codebuild:UpdateReport",
                        "codebuild:BatchPutTestCases",
                        "codebuild:BatchPutCodeCoverages",
                    ],
                    resources=[report_group.report_group_arn],
                )
            ],
        )

    def validate_integration_tests(self):
        return pipelines.CodeBuildStep(
            "Validate Integration Tests",
            input=self.source,
            install_commands=[
                "pip install -r requirements.txt",
            ],
            commands=[
                "pytest -m integration --collect-only . -q || echo 'No integration tests found, continuing...'",
                "python validate_integration_tests.py",
            ],
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
            ),
        )

    def validate_docs(self):
        return pipelines.CodeBuildStep(
            "Validate Docs",
            input=self.source,
            install_commands=[
                "pip install -r requirements.txt",
            ],
            commands=[
                "python validate_docs.py",
            ],
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
            ),
        )

    def run_integration_tests(self):
        report_group = codebuild.ReportGroup(
            self.scope,
            "IntegrationReportGroup",
        )

        return pipelines.CodeBuildStep(
            "Integration Test",
            input=self.source,
            install_commands=[
                "pip install -r requirements.txt",
            ],
            commands=[
                'pytest --junitxml=pytest-report/test-results.xml -k "integration.py"'
            ],
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(
                {
                    "reports": {
                        report_group.report_group_arn: {
                            "files": "test-results.xml",
                            "base-directory": "pytest-report",
                            "file-format": "JUNITXML",
                        }
                    }
                }
            ),
            role_policy_statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "dynamodb:PutItem",
                        "dynamodb:GetItem",
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:DeleteItem",
                    ],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["secretsmanager:GetSecretValue"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["kms:Decrypt"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "codebuild:CreateReportGroup",
                        "codebuild:CreateReport",
                        "codebuild:UpdateReport",
                        "codebuild:BatchPutTestCases",
                        "codebuild:BatchPutCodeCoverages",
                    ],
                    resources=[report_group.report_group_arn],
                ),
            ],
        )

    def generate_docs(self, name, stage):
        bucket = self.scope.node.try_get_context("bucket")
        return pipelines.CodeBuildStep(
            f"Generate {stage} Docs",
            input=self.source,
            install_commands=[
                "pip install -r requirements.txt",
            ],
            commands=[
                "python generate_docs.py",
                "python swagger_yml_to_ui.py < docs.yaml > swagger.html",
                f"aws s3 cp swagger.html s3://{bucket}/{name}/{stage.lower()}-swagger.html",
            ],
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
            ),
            role_policy_statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:PutObject",
                        "s3:PutObjectAcl",
                    ],
                    resources=["*"],
                )
            ],
        )
