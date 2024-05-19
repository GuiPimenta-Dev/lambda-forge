from aws_cdk import pipelines as pipelines

from lambda_forge.codebuild import CodeBuild


class CodeBuildSteps:
    def __init__(self, scope, context, source):
        self.context = context
        self.codebuild = CodeBuild(scope, context, source)
        self.bucket = f"{context.bucket}/{context.name}/{context.stage.lower()}"
        self.s3_permissions = [
            {
                "actions": [
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                ],
                "resources": [f"arn:aws:s3:::{self.bucket}/*"],
            }
        ]

    def unit_tests(self, name="UnitTests", permissions=[]):

        return self.codebuild.create_step(
            name=name,
            permissions=permissions,
            commands=['pytest --junitxml=test-results.xml -k "unit.py"'],
        )

    def coverage(self, name="Coverage", permissions=[]):

        return self.codebuild.create_step(
            name=name,
            permissions=permissions,
            commands=[
                'coverage run -m pytest -k "unit.py"',
                f"coverage xml --fail-under={self.context.coverage}",
                "touch coverage.xml",
            ],
        )

    def validate_docs(self, name="ValidateDocs"):

        return self.codebuild.create_step(
            name=name,
            commands=["cdk synth", "python validate_docs.py"],
        )

    def validate_integration_tests(self, name="ValidateIntegrationTests"):

        return self.codebuild.create_step(
            name=name,
            commands=[
                "cdk synth",
                "echo 'from additional_fixtures import *' >> conftest.py",
                "pytest -m integration --collect-only . -q",
                "python validate_integration_tests.py",
            ],
        )

    def integration_tests(self, name="IntegrationTests", permissions=[]):

        return self.codebuild.create_step(
            name=name,
            permissions=permissions,
            commands=['pytest --junitxml=test-results.xml -k "integration.py"'],
        )

    def swagger(self, name="Swagger"):
        return self.codebuild.create_step(
            name=name,
            permissions=self.s3_permissions,
            commands=[
                "cdk synth",
                "python generate_swagger.py",
                f"aws s3 cp swagger.html s3://{self.bucket}/swagger.html",
            ],
        )

    def redoc(self, name="Redoc", permissions=[]):
        return self.codebuild.create_step(
            name=name,
            permissions=self.s3_permissions + permissions,
            commands=[
                "cdk synth",
                "python generate_redoc.py",
                f"aws s3 cp redoc.html s3://{self.bucket}/redoc.html",
            ],
        )

    def diagram(self, name="Diagram", permissions=[]):
        return self.codebuild.create_step(
            name=name,
            permissions=self.s3_permissions + permissions,
            commands=[
                "forge diagram",
                "python embed_image_in_html.py diagram.png diagram.html",
                f"aws s3 cp diagram.html s3://{self.bucket}/diagram.html",
            ],
        )

    def wikis(self, wikis, name="Wikis", permissions=[]):
        commands = []
        for wiki in wikis:
            file_path = wiki["file_path"]
            title = wiki["title"].title()
            favicon = wiki.get("favicon", "favicon.png")
            commands.append(f"python generate_wiki.py '{file_path}' '{title}' '{favicon}'")
            commands.append(f"aws s3 cp {title}.html s3://{self.bucket}/{title.lower()}.html")

        return self.codebuild.create_step(
            name=name,
            permissions=self.s3_permissions + permissions,
            commands=commands,
        )

    def tests_report(self, name="TestsReport", permissions=[]):
        return self.codebuild.create_step(
            name=name,
            permissions=self.s3_permissions + permissions,
            commands=[
                "echo 'from additional_fixtures import *' >> conftest.py",
                "pytest --html=tests.html --self-contained-html || echo 'skipping failure'",
                f"aws s3 cp tests.html s3://{self.bucket}/tests.html",
            ],
        )

    def coverage_report(self, name="CoverageReport", permissions=[]):
        return self.codebuild.create_step(
            name=name,
            permissions=self.s3_permissions + permissions,
            commands=[
                "coverage run -m pytest || echo 'skipping failure'",
                "coverage html",
                f"aws s3 cp htmlcov/index.html s3://{self.bucket}/coverage.html",
            ],
        )

    def custom_step(
        self,
        name,
        commands,
        permissions=[],
        docker_registry="public.ecr.aws/x8r4y7j7/lambda-forge:latest",
        install_commands=[],
        env={},
        partial_build_spec={},
        requirements="requirements.txt",
    ):
        return self.codebuild.create_step(
            name=name,
            commands=commands,
            docker_registry=docker_registry,
            install_commands=install_commands,
            partial_build_spec=partial_build_spec,
            permissions=permissions,
            requirements=requirements,
            env=env,
        )
