from lambda_forge.main import project
from click.testing import CliRunner

from tests.conftest import file_exists, read_lines, created_files

runner = CliRunner()


def test_it_should_raise_an_error_when_bucket_is_none_and_no_doc_is_false():

    result = runner.invoke(
        project, ["project_name", "--repo-owner", "owner", "--repo-name", "repo"]
    )

    assert (
        result.output
        == "Usage: project [OPTIONS] NAME\nTry 'project --help' for help.\n\nError: You must provide a S3 bucket for the docs or use the flag --no-docs\n"
    )


def test_it_should_not_create_dev_stack_when_no_dev_is_true():

    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--no-dev",
            "--bucket",
            "bucket",
        ],
    )

    app = read_lines("app.py")
    assert "from infra.stacks.dev_stack import DevStack" not in app
    assert file_exists("infra/stacks/dev_stack.yml") == False


def test_it_should_not_create_staging_stack_when_no_staging_is_true():

    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--no-staging",
            "--bucket",
            "bucket",
        ],
    )

    app = read_lines("app.py")
    assert "from infra.stacks.staging_stack import StagingStack" not in app
    assert file_exists("infra/stacks/staging_stack.yml") == False


def test_it_should_not_create_prod_stack_when_no_prod_is_true():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--no-prod",
            "--bucket",
            "bucket",
        ],
    )
    app = read_lines("app.py")
    assert "from infra.stacks.prod_stack import ProdStack" not in app
    assert file_exists("infra/stacks/prod_stack.yml") == False


def test_it_should_create_the_files_when_asking_for_docs():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--bucket",
            "bucket",
        ],
    )
    files = created_files(".")
    assert files == [
        "./generate_docs.py",
        "./conftest.py",
        "./pytest.ini",
        "./requirements.txt",
        "./.pre-commit-config.yaml",
        "./cdk.context.json",
        "./cdk.json",
        "./__init__.py",
        "./.coveragerc",
        "./source.bat",
        "./validate_docs.py",
        "./swagger_yml_to_ui.py",
        "./.gitignore",
        "./app.py",
        "./validate_integration_tests.py",
        "./infra/__init__.py",
        "./infra/stacks/staging_stack.py",
        "./infra/stacks/lambda_stack.py",
        "./infra/stacks/__init__.py",
        "./infra/stacks/prod_stack.py",
        "./infra/stacks/dev_stack.py",
        "./infra/stages/__init__.py",
        "./infra/steps/__init__.py",
        "./infra/steps/code_build_step.py",
        "./infra/services/api_gateway.py",
        "./infra/services/aws_lambda.py",
        "./infra/services/__init__.py",
        "./functions/__init__.py",
        "./functions/docs/config.py",
        "./functions/docs/__init__.py",
        "./functions/authorizer/__init__.py",
        "./functions/authorizer/docs_authorizer/config.py",
        "./functions/authorizer/docs_authorizer/__init__.py",
        "./functions/authorizer/docs_authorizer/unit.py",
        "./functions/authorizer/docs_authorizer/main.py",
        "./functions/authorizer/utils/__init__.py",
    ]
