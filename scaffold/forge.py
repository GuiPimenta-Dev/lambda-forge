import click

from function_builder import FunctionBuilder
from project_builder import ProjectBuilder


@click.group()
def forge():
    pass


@forge.command()
@click.argument("name")
@click.option("--description", required=True, help="Description for the endpoint")
@click.option(
    "--method", required=False, help="HTTP method for the endpoint", default=None)
@click.option("--belongs", help="Folder name you want to share code accross lambdas")
@click.option("--endpoint", help="Endpoint URL for the API Gateway")
@click.option("--no-api", help="Do not create an API Gateway endpoint", is_flag=True)
def create(name, description, method, belongs, endpoint, no_api):
    """
    Creates the required folder structure with the given name.
    """
    create_function(name, description, method.upper(), belongs, endpoint, no_api)

def create_function(
    name, description, http_method=None, belongs=None, endpoint=None, no_api=False
):
    if no_api is False and not http_method:
        raise click.UsageError("You must provide a method for the API Gateway endpoint or use the flag --no-api")
    
    function_builder = FunctionBuilder.a_function(name, description).with_config(belongs)

    if no_api is False:
        endpoint = endpoint or belongs or name
        function_builder = function_builder.with_endpoint(endpoint).with_api(http_method).with_integration(http_method)
    
    function_builder = function_builder.with_unit().with_main().with_lambda_stack()
    function_builder.build()
    


@forge.command()
def start():
    """
    Starts the project structure
    """
    create_project()


def create_project():
    
    project_builder = ProjectBuilder.a_project()

    project_builder.build()
    

if __name__ == "__main__":
    # forge()
    create_project()
