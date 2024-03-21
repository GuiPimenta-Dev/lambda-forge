import click

from lambda_forge.authorizer_builder import AuthorizerBuilder
from lambda_forge.function_builder import FunctionBuilder
from lambda_forge.project_builder import ProjectBuilder
from lambda_forge.service_builder import ServiceBuilder


@click.group()
def forge():
    pass


@forge.command()
@click.argument("name")
@click.option("--repo-owner", help="Owner of the repository", required=True)
@click.option("--repo-name", help="Repository name", required=True)
@click.option(
    "--no-dev", help="Do not create a dev environment", is_flag=True, default=False
)
@click.option(
    "--no-staging",
    help="Do not create a staging environment",
    is_flag=True,
    default=False,
)
@click.option(
    "--no-prod", help="Do not create a prod environment", is_flag=True, default=False
)
@click.option(
    "--no-docs",
    help="Do not create documentation for the api endpoints",
    is_flag=True,
    default=False,
)
@click.option(
    "--public-docs",
    help="Create public documentation for the api endpoints",
    is_flag=True,
    default=False,
)
@click.option(
    "--bucket",
    help="Bucket used to store the documentation",
    default="",
)
@click.option(
    "--coverage",
    help="Minimum coverage percentage",
    default=80,
)
def project(
    name,
    repo_owner,
    repo_name,
    no_dev,
    no_staging,
    no_prod,
    no_docs,
    public_docs,
    bucket,
    coverage,
):
    """
    Forges the initial project structure.
    """

    if no_docs is False and not bucket:
        raise click.UsageError(
            "You must provide a S3 bucket for the docs or use the flag --no-docs"
        )

    create_project(
        name,
        repo_owner,
        repo_name,
        no_dev,
        no_staging,
        no_prod,
        no_docs,
        public_docs,
        bucket,
        coverage,
    )


def create_project(
    name,
    repo_owner,
    repo_name,
    no_dev,
    no_staging,
    no_prod,
    no_docs,
    public_docs,
    bucket,
    coverage,
):

    project_builder = ProjectBuilder.a_project(name, not no_docs)

    if no_dev is False:
        project_builder = project_builder.with_dev()

    if no_staging is False:
        project_builder = project_builder.with_staging()

    if no_prod is False:
        project_builder = project_builder.with_prod()

    project_builder = (
        project_builder.with_app()
        .with_cdk(repo_owner, repo_name, bucket, coverage)
        .with_gitignore()
        .with_pytest_ini()
        .with_pre_commit()
        .with_coverage()
    )
    project_builder.build()

    if no_docs is False:

        if public_docs is False:
            AuthorizerBuilder.an_authorizer(
                "docs_authorizer",
                "Function used to authorize the docs endpoints",
                "authorizers",
            ).with_config().with_main().with_unit().with_lambda_stack().build()

        custom_config = f"""
from infra.services import Services

class DocsConfig:

    def __init__(self, scope, services: Services) -> None:
        bucket = scope.node.try_get_context("bucket")
        services.api_gateway.create_docs(bucket=bucket, authorizer={None if public_docs else '"docs_authorizer"'})
"""

        FunctionBuilder.a_function("docs").with_custom_config(
            custom_config
        ).with_lambda_stack(docs=True).build()


@forge.command()
@click.argument("name")
@click.option("--description", required=True, help="Description for the endpoint")
@click.option(
    "--method", required=False, help="HTTP method for the endpoint", default=None
)
@click.option("--belongs", help="Folder name you want to share code accross lambdas")
@click.option("--endpoint", help="Endpoint for the API Gateway")
@click.option("--no-api", help="Do not create an API Gateway endpoint", is_flag=True)
@click.option(
    "--public",
    help="Endpoint is public",
    is_flag=True,
    default=False,
)
def function(name, description, method, belongs, endpoint, no_api, public):
    """
    Forjes a function with the required folder structure.
    """
    method = method.upper() if method else None
    create_function(name, description, method, belongs, endpoint, no_api, public)


def create_function(
    name,
    description,
    http_method=None,
    belongs=None,
    endpoint=None,
    no_api=False,
    public=False,
):
    if no_api is False and not http_method:
        raise click.UsageError(
            "You must provide a method for the API Gateway endpoint or use the flag --no-api"
        )

    function_builder = FunctionBuilder.a_function(name, description).with_config(
        belongs
    )

    if no_api is True:
        function_builder = function_builder.with_unit().with_main()

    elif no_api is False:
        endpoint = endpoint or belongs or name
        function_builder = (
            function_builder.with_endpoint(endpoint)
            .with_api(http_method, public)
            .with_integration(http_method)
            .with_unit()
            .with_main()
        )

    function_builder = function_builder.with_lambda_stack()
    function_builder.build()


@forge.command()
@click.argument("name")
@click.option("--description", required=True, help="Description for the endpoint")
@click.option(
    "--default",
    help="Mark the authorizer as the default for all private endpoints with no authorizer set.",
    is_flag=True,
    default=False,
)
def authorizer(name, description, default):
    """
    Forjes an authorizer with the required folder structure.
    """
    create_authorizer(name, description, default)


def create_authorizer(name, description, default):
    authorizer_builder = AuthorizerBuilder.an_authorizer(
        name, description, "authorizers"
    )

    authorizer_builder.with_config(
        default
    ).with_main().with_unit().with_lambda_stack().build()


AVALABLE_SERVICES = sorted(
    [
        "sns",
        "dynamodb",
        "s3",
        "layers",
        "state_machine",
        "event_bridge",
        "sqs",
        "secrets_manager",
        "cognito",
        "kms",
    ]
)


@forge.command()
@click.argument(
    "service",
    type=click.Choice(AVALABLE_SERVICES),
)
def service(service):
    """
    Forjes the structure of a service.

    """
    create_service(service)


def create_service(service):
    service_builder = ServiceBuilder.a_service()

    services = {
        "sns": service_builder.with_sns,
        "layers": service_builder.with_layers,
        "dynamodb": service_builder.with_dynamodb,
        "s3": service_builder.with_s3,
        "state_machine": service_builder.with_state_machine,
        "event_bridge": service_builder.with_event_bridge,
        "sqs": service_builder.with_sqs,
        "secrets_manager": service_builder.with_secrets_manager,
        "cognito": service_builder.with_cognito,
        "kms": service_builder.with_kms,
    }
    service_builder = services[service]()

    service_builder.build()


if __name__ == "__main__":
    forge()
