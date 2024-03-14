import click

from lambda_forge.function_builder import FunctionBuilder
from lambda_forge.project_builder import ProjectBuilder
from lambda_forge.service_builder import ServiceBuilder


@click.group()
def forge():
    pass


@forge.command()
@click.argument("name")
@click.option("--description", required=True, help="Description for the endpoint")
@click.option(
    "--method", required=False, help="HTTP method for the endpoint", default=None
)
@click.option("--belongs", help="Folder name you want to share code accross lambdas")
@click.option("--endpoint", help="Endpoint URL for the API Gateway")
@click.option("--no-api", help="Do not create an API Gateway endpoint", is_flag=True)
@click.option("--authorizer", help="Define the function as an authorizer", is_flag=True)
def function(name, description, method, belongs, endpoint, no_api, authorizer):
    """
    Forjes the function with the required folder structure.
    """
    method = method.upper() if method else None
    create_function(name, description, method, belongs, endpoint, no_api, authorizer)


def create_function(
    name,
    description,
    http_method=None,
    belongs=None,
    endpoint=None,
    no_api=False,
    authorizer=False,
):
    if no_api is False and not http_method and authorizer is False:
        raise click.UsageError(
            "You must provide a method for the API Gateway endpoint or use the flag --no-api"
        )

    if authorizer:
        belongs = belongs or "authorizer"

    function_builder = FunctionBuilder.a_function(name, description).with_config(
        belongs
    )

    if authorizer:
        function_builder.with_authorizer().with_authorizer_unit()

    elif no_api is True:
        function_builder = function_builder.with_unit().with_main()

    elif no_api is False:
        endpoint = endpoint or belongs or name
        function_builder = (
            function_builder.with_endpoint(endpoint)
            .with_api(http_method)
            .with_integration(http_method)
            .with_unit()
            .with_main()
        )

    function_builder = function_builder.with_lambda_stack()
    function_builder.build()


@forge.command()
@click.option(
    "--no-dev", help="Do not create dev environment", is_flag=True, default=False
)
@click.option(
    "--no-staging",
    help="Do not create staging environment",
    is_flag=True,
    default=False,
)
@click.option(
    "--no-prod", help="Do not create prod environment", is_flag=True, default=False
)
@click.option(
    "--no-docs",
    help="Do not create documentation for the api endpoints",
    is_flag=True,
    default=False,
)
def project(no_dev, no_staging, no_prod, no_docs):
    """
    Forjes the project structure.
    """
    create_project(no_dev, no_staging, no_prod, no_docs)


def create_project(no_dev, no_staging, no_prod, no_docs):
    project_builder = ProjectBuilder.a_project()

    if no_docs is False:
        project_builder = project_builder.with_docs()

    if no_dev is False:
        project_builder = project_builder.with_dev()

    if no_staging is False:
        project_builder = project_builder.with_staging()

    if no_prod is False:
        project_builder = project_builder.with_prod()

    project_builder = project_builder.with_app()
    project_builder.build()


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
