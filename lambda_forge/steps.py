import os
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_iam as iam
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
import pkg_resources


class Steps:
    def __init__(self, scope, context, source: CodePipelineSource):
        self.scope = scope
        self.context = context
        self.source = source

    def run_unit_tests(self, env={}, role_policy_statements=[]):
        report_group = codebuild.ReportGroup(
            self.scope,
            "UnitReportGroup",
        )

        return pipelines.CodeBuildStep(
            "Unit Test",
            input=self.source,
            install_commands=[
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                "pip install -r requirements.txt",
            ],
            commands=[
                'pytest --junitxml=pytest-report/test-results.xml -k "unit.py"',
            ],
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            env=env,
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables=env,
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(
                {
                    "reports": {
                        report_group.report_group_arn: {
                            "files": "test-results.xml",
                            "base-directory": "pytest-report",
                            "file-format": "JUNITXML",
                        }
                    },
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
            ]
            + role_policy_statements,
        )

    def run_coverage(self, env={}, role_policy_statements=[]):
        report_group = codebuild.ReportGroup(
            self.scope,
            "CoverageGroup",
            type=codebuild.ReportGroupType.CODE_COVERAGE,
        )
        return pipelines.CodeBuildStep(
            "Coverage",
            input=self.source,
            install_commands=[
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                "pip install -r requirements.txt",
            ],
            env=env,
            commands=[
                'coverage run -m pytest -k "unit.py"',
                f"coverage xml --fail-under={self.context.coverage}",
                "touch coverage.xml",
            ],
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables=env,
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(
                {
                    "cache": {
                        "paths": [
                            "/root/.cache/pip/**/*",
                        ]
                    },
                    "reports": {
                        report_group.report_group_arn: {
                            "files": "coverage.xml",
                            "base-directory": ".",
                            "file-format": "COBERTURAXML",
                        }
                    },
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
            ]
            + role_policy_statements,
        )

    def validate_integration_tests(self, env={}, role_policy_statements=[]):
        validate_integration_tests = pkg_resources.resource_string(__name__, "validate_integration_tests.py")

        conftest = """import json 
def pytest_generate_tests(metafunc):
    for mark in metafunc.definition.iter_markers(name="integration"):
        with open("tested_endpoints.txt", "a") as f:
            f.write(f"{json.dumps(mark.kwargs)}|")"""

        env = {"TRACK": "true"} | env

        return pipelines.CodeBuildStep(
            "Validate Integration Tests",
            input=self.source,
            install_commands=[
                "npm install -g aws-cdk",
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                "pip install -r requirements.txt",
            ],
            env=env,
            commands=[
                "cdk synth",
                "rm -rf cdk.out",
                f"echo '{conftest}' > conftest.py",
                f"echo '{validate_integration_tests.decode()}' > validate_integration_tests.py",
                "pytest -m integration --collect-only . -q",
                "python validate_integration_tests.py",
            ],
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(
                {
                    "cache": {
                        "paths": [
                            "/root/.cache/pip/**/*",
                        ]
                    },
                }
            ),
            role_policy_statements=role_policy_statements,
        )

    def validate_docs(self, env={}, role_policy_statements=[]):
        validate_docs = pkg_resources.resource_string(__name__, "validate_docs.py")
        env = {"TRACK": "true"} | env

        return pipelines.CodeBuildStep(
            "Validate Docs",
            input=self.source,
            install_commands=[
                "npm install -g aws-cdk",
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                "pip install -r requirements.txt",
            ],
            commands=[
                "cdk synth",
                "rm -rf cdk.out",
                f"echo '{validate_docs.decode()}' > validate_docs.py",
                "python validate_docs.py",
            ],
            env=env,
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
            ),
            role_policy_statements=role_policy_statements,
        )

    def run_integration_tests(self, env={}, role_policy_statements=[]):
        report_group = codebuild.ReportGroup(
            self.scope,
            "IntegrationReportGroup",
        )
        role_policy_statements = [
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
        ] + role_policy_statements
        return pipelines.CodeBuildStep(
            "Integration Test",
            input=self.source,
            install_commands=[
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                "pip install -r requirements.txt",
            ],
            env=env,
            commands=['pytest --junitxml=pytest-report/test-results.xml -k "integration.py"'],
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables=env,
            ),
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            partial_build_spec=codebuild.BuildSpec.from_object(
                {
                    "reports": {
                        report_group.report_group_arn: {
                            "files": "test-results.xml",
                            "base-directory": "pytest-report",
                            "file-format": "JUNITXML",
                        }
                    },
                }
            ),
            role_policy_statements=role_policy_statements,
        )

    def generate_docs(self, stage=None, env={}, role_policy_statements=[]):
        stage = stage or self.context.stage
        generate_docs = pkg_resources.resource_string(__name__, "generate_docs.py")
        swagger_yml_to_ui = pkg_resources.resource_string(__name__, "swagger_yml_to_ui.py")
        generate_diagram = pkg_resources.resource_string(__name__, "generate_diagram.py")
        bucket = self.scope.node.try_get_context("bucket")

        env = {"TRACK": "true"} | env
        return pipelines.CodeBuildStep(
            f"Generate {stage} Docs",
            input=self.source,
            install_commands=[
                "npm install -g aws-cdk",
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                "pip install -r requirements.txt pytest-html coverage",
                "npm install -g redoc-cli cdk-dia",
                "sudo apt install -y graphviz",
            ],
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            env=env,
            commands=[
                "cdk synth",
                "rm -rf cdk.out",
                f"echo '{generate_docs.decode()}' > generate_docs.py",
                "python generate_docs.py",
                f"echo '{swagger_yml_to_ui.decode()}' > swagger_yml_to_ui.py",
                "python swagger_yml_to_ui.py < docs.yaml > swagger.html",
                "redoc-cli bundle -o redoc.html docs.yaml",
                f"echo '{generate_diagram.decode()}' > generate_diagram.py",
                f"python generate_diagram.py {self.context.stage}",
                f"aws s3 cp swagger.html s3://{bucket}/{self.context.name}/{self.context.stage.lower()}-swagger.html",
                f"aws s3 cp redoc.html s3://{bucket}/{self.context.name}/{self.context.stage.lower()}-redoc.html",
                f"aws s3 cp diagram.png s3://{bucket}/{self.context.name}/{self.context.stage.lower()}-diagram.png",
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
            ]
            + role_policy_statements,
        )
