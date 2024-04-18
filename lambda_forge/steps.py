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

    def run_unit_tests(
        self,
        name="Unit Tests",
        stage=None,
        report_group_name=None,
        env={},
        role_policy_statements=[],
        requirements="requirements.txt",
    ):

        stage = stage or self.context.stage

        report_group_name = report_group_name or f"{stage}-{self.context.name}-UnitReportGroup"
        report_group = codebuild.ReportGroup(
            self.scope,
            report_group_name,
        )

        return pipelines.CodeBuildStep(
            name,
            input=self.source,
            install_commands=[
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                f"pip install -r {requirements}",
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

    def run_coverage(
        self,
        name="Coverage",
        report_group_name=None,
        stage=None,
        env={},
        role_policy_statements=[],
        requirements="requirements.txt",
    ):
        stage = stage or self.context.stage
        report_group_name = report_group_name or f"{stage}-{self.context.name}-CoverageReportGroup"
        report_group = codebuild.ReportGroup(
            self.scope,
            report_group_name,
            type=codebuild.ReportGroupType.CODE_COVERAGE,
        )
        return pipelines.CodeBuildStep(
            name,
            input=self.source,
            install_commands=[
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                f"pip install -r {requirements} coverage pytest",
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

    def validate_integration_tests(
        self, name="Validate Integration Tests", env={}, role_policy_statements=[], requirements="requirements.txt"
    ):
        validate_integration_tests = pkg_resources.resource_string(__name__, "validate_integration_tests.py")

        conftest = """import json 
def pytest_generate_tests(metafunc):
    for mark in metafunc.definition.iter_markers(name="integration"):
        with open("tested_endpoints.txt", "a") as f:
            f.write(f"{json.dumps(mark.kwargs)}|")"""

        env = {"TRACK": "true"} | env

        return pipelines.CodeBuildStep(
            name,
            input=self.source,
            install_commands=[
                "npm install -g aws-cdk",
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                f"pip install -r {requirements}",
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

    def validate_docs(self, name="Validate Docs", env={}, role_policy_statements=[], requirements="requirements.txt"):
        validate_docs = pkg_resources.resource_string(__name__, "validate_docs.py")
        env = {"TRACK": "true"} | env

        return pipelines.CodeBuildStep(
            name,
            input=self.source,
            install_commands=[
                "npm install -g aws-cdk",
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                f"pip install -r {requirements}",
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

    def run_integration_tests(
        self,
        name="Integration Test",
        report_group_name=None,
        stage=None,
        env={},
        role_policy_statements=[],
        requirements="requirements.txt",
    ):
        stage = stage or self.context.stage
        report_group_name = report_group_name or f"{stage}-{self.context.name}-IntegrationReportGroup"
        report_group = codebuild.ReportGroup(self.scope, report_group_name)
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
            name,
            input=self.source,
            install_commands=[
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                "forge layer --install",
                f"pip install -r {requirements}",
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

    def generate_docs(
        self,
        name="Generate Docs",
        stage=None,
        env={},
        role_policy_statements=[],
        requirements="requirements.txt",
        api=True,
        diagram=True,
        tests=True,        
        todo=True,
        wikis=[],
    ):
        stage = stage or self.context.stage
        generate_docs = pkg_resources.resource_string(__name__, "generate_docs.py")
        swagger_yml_to_ui = pkg_resources.resource_string(__name__, "swagger_yml_to_ui.py")
        generate_diagram = pkg_resources.resource_string(__name__, "generate_diagram.py")
        embed_image_in_html = pkg_resources.resource_string(__name__, "embed_image_in_html.py")
        generate_wiki = pkg_resources.resource_string(__name__, "generate_wiki.py")
        # pytest_html_styles = pkg_resources.resource_string(__name__, "pytests_html_styles.css")
        # todo = pkg_resources.resource_string(__name__, "generate_todo.py")


        commands = ["cdk synth", "rm -rf cdk.out"]

        if api:
            api_commands = [
                f"echo '{generate_docs.decode()}' > generate_docs.py",
                "python generate_docs.py",
                f"echo '{swagger_yml_to_ui.decode()}' > swagger_yml_to_ui.py",
                "python swagger_yml_to_ui.py < docs.yaml > swagger.html",
                "redoc-cli bundle -o redoc.html docs.yaml",
                f"aws s3 cp swagger.html s3://{self.context.bucket}/{self.context.name}/{stage.lower()}/swagger.html",
                f"aws s3 cp redoc.html s3://{self.context.bucket}/{self.context.name}/{stage.lower()}/redoc.html",
            ]
            commands += api_commands

        if diagram:
            diagram_commands = [
                f"echo '{generate_diagram.decode()}' > generate_diagram.py",
                f"python generate_diagram.py {stage}",
                f"echo '{embed_image_in_html.decode()}' > embed_image_in_html.py",
                "python embed_image_in_html.py diagram.png diagram.html",
                f"aws s3 cp diagram.html s3://{self.context.bucket}/{self.context.name}/{stage.lower()}/diagram.html",
            ]
            commands += diagram_commands


        # if todo:
        #     todo_commands = [
        #         f"echo '{todo.decode()}' > generate_todo.py",
        #         "python generate_todo.py",
        #         f"aws s3 cp todo.html s3://{self.context.bucket}/{self.context.name}/{stage.lower()}/todo.html",
        #     ]
        #     commands += todo_commands

        if wikis:
            wikis_commands = [
                f"echo '{generate_wiki.decode()}' > generate_wiki.py",
            ]
            for wiki in wikis:
                file_path = wiki.get("file_path", "")
                title = wiki.get("title", "Wiki").title()
                favicon = wiki.get("favicon", "favicon.png")
                wikis_commands.append(f"python generate_wiki.py '{file_path}' '{title}' '{favicon}'")
                wikis_commands.append("ls")
                wikis_commands.append(f"cat {title}.html")
                wikis_commands.append(
                    f"aws s3 cp {title}.html s3://{self.context.bucket}/{self.context.name}/{stage.lower()}/{title.lower()}.html"
                )
                wikis_commands.append(
                    f"aws s3 cp {title}.html s3://{self.context.bucket}/{self.context.name}/funciona.html"
                )
                wikis_commands.append(f"cat {title}.html")

            commands += wikis_commands

        if tests:
            
            conftest = f"""def pytest_html_report_title(report):
    report.title = "Test Report"
"""
            
            test_commands = [
                f"echo '{conftest}' > conftest.py",
                "rm -rf cdk.out",
                "rm -rf __pycache__/",
                # f"echo '{pytest_html_styles.decode()}' > pytests_html_styles.css",
                "coverage run -m pytest --html=report.html --self-contained-html || echo 'skipping failure'",
                "rm -rf cdk.out",
                "coverage html",
                f"aws s3 cp report.html s3://{self.context.bucket}/{self.context.name}/{stage.lower()}/tests.html",
                f"aws s3 cp htmlcov/index.html s3://{self.context.bucket}/{self.context.name}/{stage.lower()}/coverage.html",
            ]
            commands += test_commands

        env = {"TRACK": "true"} | env
        return pipelines.CodeBuildStep(
            name,
            input=self.source,
            install_commands=[
                "npm install -g aws-cdk",
                "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/ --upgrade",
                "forge layer --install",
                f"pip install -r {requirements} pytest-html coverage",
                "npm install -g redoc-cli cdk-dia",
                "sudo apt install -y graphviz",
            ],
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            env=env,
            commands=commands,
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
