from aws_cdk import pipelines as pipelines

from infra.steps.codebuild import CodeBuild


class Steps:
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

    def run_unit_tests(self):
        
        report_group = {
            "name": "UnitTestsReport",
            "files": "test-results.xml",
            "file_format": "JUNITXML",
            "file_type": "test",
        }
        
        return self.codebuild.create_step(
            name="UnitTests",
            commands=['pytest --junitxml=test-results.xml -k "unit.py"'],
            report_group=report_group,
        )

    def run_coverage(self):
        
        report_group = {
            "name": "CoverageReport",
            "files": "coverage.xml",
            "file_format": "COBERTURAXML",
            "file_type": "coverage",
        }

        return self.codebuild.create_step(
            name="Coverage",
            report_group=report_group,
            commands=[
                'coverage run -m pytest -k "unit.py"',
                f"coverage xml --fail-under={self.context.coverage}",
                "touch coverage.xml",
            ],
        )

    def validate_docs(self):
        
        return self.codebuild.create_step(
            name="ValidateDocs",
            commands=["cdk synth", "python validate_docs.py"],
        )

    def validate_integration_tests(self):
        
        return self.codebuild.create_step(
            name="ValidateIntegrationTests",
            commands=[
                "cdk synth",
                "echo 'from additional_fixtures import *' >> conftest.py",
                "pytest -m integration --collect-only . -q",
                "python validate_integration_tests.py",
            ],
        )

    def run_integration_tests(self):
        
        report_group = {
            "name": "IntegrationTestsReport",
            "files": "test-results.xml",
            "file_format": "JUNITXML",
            "file_type": "test",
        }

        return self.codebuild.create_step(
            name="IntegrationTests",
            report_group=report_group,
            commands=['pytest --junitxml=test-results.xml -k "integration.py"'],
        )

    def swagger(self):
        return self.codebuild.create_step(
            name="Swagger",
            permissions=self.s3_permissions,
            commands=[
                "cdk synth",
                "python generate_swagger.py",
                f"aws s3 cp swagger.html s3://{self.bucket}/swagger.html",
            ],
        )

    def redoc(self):
        return self.codebuild.create_step(
            name="Redoc",
            permissions=self.s3_permissions,
            commands=[
                "cdk synth",
                "python generate_redoc.py",
                f"aws s3 cp redoc.html s3://{self.bucket}/redoc.html",
            ],
        )

    def diagram(self):
        return self.codebuild.create_step(
            name="Diagram",
            permissions=self.s3_permissions,
            commands=[
                f"python generate_diagram.py {self.context.stage}",
                f"aws s3 cp diagram.html s3://{self.bucket}/diagram.html",
            ],
        )

    def wikis(self, wikis=[]):
        commands = []
        for wiki in wikis:
            file_path = wiki["file_path"]
            title = wiki["title"].title()
            favicon = wiki.get("favicon", "favicon.png")
            commands.append(f"python generate_wiki.py '{file_path}' '{title}' '{favicon}'")
            commands.append(f"aws s3 cp {title}.html s3://{self.bucket}/{title.lower()}.html")

        return self.codebuild.create_step(
            name="Wikis",
            permissions=self.s3_permissions,
            commands=commands,
        )

    def tests_report(self):
        return self.codebuild.create_step(
            name="TestsReport",
            permissions=self.s3_permissions,
            commands=[
                "echo 'from additional_fixtures import *' >> conftest.py",
                "pytest --html=tests.html --self-contained-html || echo 'skipping failure'",
                f"aws s3 cp tests.html s3://{self.bucket}/tests.html",
            ],
        )

    def coverage_report(self):
        return self.codebuild.create_step(
            name="CoverageReport",
            permissions=self.s3_permissions,
            commands=[
                "coverage run -m pytest || echo 'skipping failure'",
                "coverage html",
                f"aws s3 cp htmlcov/index.html s3://{self.bucket}/coverage.html",
            ],
        )
