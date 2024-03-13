import click

from forge.function_builder import FunctionBuilder
from forge.project_builder import ProjectBuilder


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
def function(name, description, method, belongs, endpoint, no_api):
    """
    Forjes the function with the required folder structure.
    """
    create_function(name, description, method.upper(), belongs, endpoint, no_api)


def create_function(
    name, description, http_method=None, belongs=None, endpoint=None, no_api=False
):
    if no_api is False and not http_method:
        raise click.UsageError(
            "You must provide a method for the API Gateway endpoint or use the flag --no-api"
        )

    function_builder = FunctionBuilder.a_function(name, description).with_config(
        belongs
    )

    if no_api is False:
        endpoint = endpoint or belongs or name
        function_builder = (
            function_builder.with_endpoint(endpoint)
            .with_api(http_method)
            .with_integration(http_method)
        )

    function_builder = function_builder.with_unit().with_main().with_lambda_stack()
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


if __name__ == "__main__":
    # forge()
    create_project(False, False, False, False)
