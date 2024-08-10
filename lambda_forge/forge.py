import json
import os
import platform
import re
import signal
import subprocess

import boto3
import click
from InquirerPy import get_style, inquirer

from lambda_forge import layers
from lambda_forge.builders.authorizer_builder import AuthorizerBuilder
from lambda_forge.builders.docs_builder import DocsBuilder
from lambda_forge.builders.function_builder import FunctionBuilder
from lambda_forge.builders.layer_builder import LayerBuilder
from lambda_forge.builders.project_builder import ProjectBuilder
from lambda_forge.builders.service_builder import ServiceBuilder
from lambda_forge.diagram import create_diagram
from lambda_forge.live import server_cli
from lambda_forge.printer import Printer


printer = Printer()


@click.group()
def forge():
    """
    Forge CLI tool for structuring and deploying AWS Lambda projects.

    This command group provides a suite of tools for building and managing AWS Lambda
    projects, including creating projects, functions, authorizers, services, and layers.
    """
    pass


@forge.command()
@click.option("--name", help="Project name")
@click.option("--repo-owner", help="Owner of the repository")
@click.option("--repo-name", help="Repository name")
@click.option(
    "--no-docs",
    help="Do not create documentation for the api endpoints",
    is_flag=True,
    default=False,
)
@click.option(
    "--minimal",
    help="Minimal project configuration",
    is_flag=True,
    default=False,
)
@click.option(
    "--account",
    help="AWS account to deploy the project",
    default="",
)
@click.option(
    "--region",
    help="AWS region to deploy the project",
    default="",
)
@click.option(
    "--bucket",
    help="Bucket used to store the documentation",
    default="",
)
def project(
    name,
    repo_owner,
    repo_name,
    no_docs,
    minimal,
    account,
    region,
    bucket,
):
    """
    Initializes a new AWS Lambda project with a specified structure.

    This command sets up the initial project structure, including development, staging,
    and production environments, API documentation, and AWS deployment configurations.

    Requires specifying a S3 bucket if API documentation is enabled.
    """

    printer.show_banner("New Project")

    if not name:
        click.echo()
        style = click.style("Project Name", fg=(37, 171, 190))
        name = click.prompt(style, type=str)

    if not repo_owner:
        click.echo()
        style = click.style("Repository Owner", fg=(37, 171, 190))
        repo_owner = click.prompt(style, type=str)

    if not repo_name:
        click.echo()
        style = click.style("Repository Name", fg=(37, 171, 190))
        repo_name = click.prompt(style, type=str)

    if account:
        click.echo()
        if not re.match(r"^\d{12}$", account):
            printer.print("Invalid Account ID. Must be a 12-digit number.", "red")
            return
    else:
        while True:
            click.echo()
            style = click.style("AWS Account ID", fg=(37, 171, 190))
            account = click.prompt(style, type=str)
            if re.match(r"^\d{12}$", account):
                break
            else:
                click.echo()
                printer.print("Invalid Account ID. Must be a 12-digit number.", "red")

    if not region:
        click.echo()
        style = click.style("AWS Region", fg=(37, 171, 190))
        region = click.prompt(style, type=str, default="us-east-2")

    if not bucket and not no_docs and not minimal:
        click.echo()

        options = ["Multi-Stage", "Multi-Stage / No Docs", "Minimal"]
        style = get_style(
            {
                "questionmark": "#25ABBE",
                "input": "#25ABBE",
                "pointer": "#25ABBE",
                "question": "#25ABBE",
                "answered_question": "#25ABBE",
                "pointer": "#25ABBE",
                "answer": "white",
                "answermark": "#25ABBE",
            },
            style_override=True,
        )
        choice = inquirer.select(
            message="Select a Project Template:",
            style=style,
            choices=options,
        ).execute()

        click.echo()
        if choice == options[0]:
            style = click.style("S3 Bucket", fg=(37, 171, 190))
            bucket = click.prompt(style, type=str)
            click.echo()
        elif choice == options[1]:
            no_docs = True
        elif choice == options[2]:
            minimal = True
            no_docs = True

    create_project(
        name,
        repo_owner,
        repo_name,
        no_docs,
        minimal,
        account,
        region,
        bucket,
    )


def create_project(
    name,
    repo_owner,
    repo_name,
    no_docs,
    minimal,
    account,
    region,
    bucket,
):

    if minimal:
        no_docs = True

    project_builder = ProjectBuilder.a_project(name, no_docs, minimal)

    project_builder = project_builder.with_cdk(
        repo_owner, repo_name, account, region, bucket
    ).build()

    if no_docs is False:
        DocsBuilder.a_doc().with_config().with_lambda_stack().build()


@forge.command()
@click.argument("name")
@click.option("--description", required=True, help="Description for the endpoint")
@click.option(
    "--method", required=False, help="HTTP method for the endpoint", default="GET"
)
@click.option("--belongs-to", help="Folder name you want to share code accross lambdas")
@click.option("--endpoint", help="Endpoint for the API Gateway")
@click.option("--no-api", help="Do not create an API Gateway endpoint", is_flag=True)
@click.option(
    "--websocket", help="Function is going to be used for websockets", is_flag=True
)
@click.option(
    "--no-tests",
    help="Do not create unit tests and integration tests files",
    is_flag=True,
    default=False,
)
@click.option(
    "--public",
    help="Endpoint is public",
    is_flag=True,
    default=False,
)
def function(
    name, description, method, belongs_to, endpoint, no_api, websocket, no_tests, public
):
    """
    Creates a Lambda function with a predefined structure and API Gateway integration.

    Sets up a new Lambda function, including configuration files, unit tests, and
    optionally an API Gateway endpoint.

    An HTTP method must be provided if an API Gateway endpoint is not skipped.
    """
    method = method.upper() if method else None
    create_function(
        name,
        description,
        method,
        belongs_to,
        endpoint,
        no_api,
        websocket,
        no_tests,
        public,
    )


def create_function(
    name,
    description,
    http_method=None,
    belongs=None,
    endpoint=None,
    no_api=False,
    websocket=False,
    no_tests=False,
    public=False,
):

    function_builder = FunctionBuilder.a_function(name, description).with_config(
        belongs
    )

    if no_api is True:
        function_builder = function_builder.with_main()
        if no_tests is False:
            function_builder = function_builder.with_unit()

    elif websocket is True:
        function_builder = function_builder.with_websocket().with_main()
        if no_tests is False:
            function_builder = function_builder.with_unit()

    else:
        endpoint = endpoint or belongs or name
        if no_tests is True:
            function_builder = (
                function_builder.with_endpoint(endpoint)
                .with_api(http_method, public)
                .with_main()
            )
        else:
            function_builder = (
                function_builder.with_endpoint(endpoint)
                .with_api(http_method, public)
                .with_integration(http_method)
                .with_unit()
                .with_main()
            )

    function_builder.with_lambda_stack().build()


@forge.command()
@click.argument("name")
@click.option("--description", required=True, help="Description for the endpoint")
@click.option(
    "--default",
    help="Mark the authorizer as the default for all private endpoints with no authorizer set.",
    is_flag=True,
    default=False,
)
@click.option(
    "--no-tests",
    help="Do not create unit tests and integration tests files",
    is_flag=True,
    default=False,
)
def authorizer(name, description, default, no_tests):
    """
    Generates an authorizer for AWS Lambda functions.

    Creates an authorizer Lambda function, including configuration and deployment setup,
    to control access to other Lambda functions.

    The authorizer can be marked as the default for all private endpoints lacking a specific authorizer.
    """
    create_authorizer(name, description, default, no_tests)


def create_authorizer(name, description, default, no_tests):
    authorizer_builder = (
        AuthorizerBuilder.an_authorizer(name, description, "authorizers", no_tests)
        .with_config(default)
        .with_main()
        .with_lambda_stack()
    )

    if no_tests is False:
        authorizer_builder = authorizer_builder.with_unit()

    authorizer_builder.build()


AVALABLE_SERVICES = sorted(
    [
        "sns",
        "dynamodb",
        "s3",
        "event_bridge",
        "sqs",
        "secrets_manager",
        "cognito",
        "kms",
        "websockets",
    ]
)


@forge.command()
@click.argument(
    "service",
    type=click.Choice(AVALABLE_SERVICES),
)
def service(service):
    """
    Scaffolds the structure for a specified AWS service integration.

    Creates boilerplate code and configuration for integrating with AWS services like
    SNS, DynamoDB, S3, etc., within the Lambda project.

    The 'service' parameter is limited to a predefined list of supported AWS services.
    """
    create_service(service)


def create_service(service):
    service_builder = ServiceBuilder.a_service()

    services = {
        "sns": service_builder.with_sns,
        "dynamodb": service_builder.with_dynamodb,
        "s3": service_builder.with_s3,
        "event_bridge": service_builder.with_event_bridge,
        "sqs": service_builder.with_sqs,
        "secrets_manager": service_builder.with_secrets_manager,
        "cognito": service_builder.with_cognito,
        "kms": service_builder.with_kms,
        "websockets": service_builder.with_websockets,
    }
    service_builder = services[service]()

    service_builder.build()


@forge.command()
@click.option(
    "--custom",
    help="Name of the custom layer to create",
)
@click.option(
    "--external",
    help="Name of the external layer to create",
)
@click.option(
    "--description",
    help="Layer description",
)
@click.option(
    "--requirements",
    help="Requirements file to install the lib",
    default="requirements.txt",
)
@click.option(
    "--install",
    help="Install all custom layers locally",
    is_flag=True,
)
def layer(custom, external, description, requirements, install):
    """
    Creates and installs a new Lambda layer.

    Sets up a new directory for the Lambda layer, prepares it for use with AWS Lambda,
    and updates the project's requirements.txt to include the new layer.

    This command facilitates layer management within the Lambda project structure.
    """
    create_layer(custom, external, description, requirements, install)


def create_layer(custom, external, description, requirements, install):
    layer_builder = LayerBuilder.a_layer().with_layers()
    print()

    if custom:
        layer_builder.with_custom_layers(custom, description)
        layers.create_and_install_package(custom)
        printer.print(f"{custom.title()} layer created", "gray", 0, 1)

    if external:
        printer.start_spinner(f"Creating Layer {external}...", "gray")
        cdk = open("cdk.json", "r").read()
        region = json.loads(cdk)["context"].get("region")
        if not region:
            printer.print("Region not found", "red", 0, 1)
            exit()

        layer_arn = layers.deploy_external_layer(external, region)
        layer_builder.with_external_layers(external, layer_arn)
        installed_version = layers.install_external_layer(external)
        layers.update_requirements_txt(requirements, f"{external}=={installed_version}")
        printer.stop_spinner()
        printer.print(f"\r{external.title()} layer ARN: {layer_arn}", "gray", 0, 1)

    layer_builder.build()

    if install:
        layers.install_all_layers()
        printer.print(f"The layers have been installed", "gray", 0, 1)


AVAILABLE_TRIGGERS = sorted(["api_gateway", "sns", "sqs", "s3", "event_bridge"])
AVAILABLE_TYPES = ["server", "logs", "trigger"]


@forge.command()
@click.option("-i", "--include", help="Include functions to watch", default=None)
@click.option("-e", "--exclude", help="Exclude functions to watch", default=None)
def live(include, exclude):
    """
    Starts a live development environment for the specified Lambda function.

    This command creates a live development environment for the specified Lambda function,
    allowing you to test and debug the function in real-time with AWS IoT Core.

    The 'function_name' parameter must match the name of an existing Lambda function in the project.
    """

    with open("live.log", "w") as f:
            f.write("")
        
    include = include.split(",") if include else None
    exclude = exclude.split(",") if exclude else None
    server_cli.run_live(include=include, exclude=exclude)
    
@forge.command()
def doc():
    """
    Creates a new doc template for the project.

    This command generates a new doc template for the project, including Swagger, Redoc, Architecture Diagram, Tests Report, and Coverage Report.
    """
    DocsBuilder.a_doc().with_config().with_lambda_stack().build()


@forge.command()
@click.option(
    "--stack",
    help="Stack to deploy",
)
@click.option("--all", help="Deploy all stacks", is_flag=True, default=False)
def deploy(stack, all):
    """
    Deploys a stack to AWS

    This command can deploys one stack or all of them altogether
    """
    if not stack and not all:
        raise Exception("You must provide a stack to deploy")

    result = subprocess.run(["cdk", "list"], capture_output=True, text=True)
    stacks = result.stdout.splitlines()
    printer.show_banner("Deployment")
    printer.br()

    if all:
        for stack in stacks:
            if "/" in str(stack):
                continue
            printer.start_spinner(f"Deploying Stack {stack}", "gray")
            try:
                subprocess.run(
                    ["cdk", "deploy", stack, "--require-approval", "never"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except Exception as e:
                printer.stop_spinner()
                printer.print(f"\r{e}", "red")
                exit()

            printer.stop_spinner()
            printer.print(f"\rStack {stack} Deployed", "green", 0, 1)

    else:

        stack_name = None
        for item in stacks:
            if stack in item:
                stack_name = item
                break

        if not stack_name:
            raise Exception(f"{stack_name} Not Found")

        printer.start_spinner(f"Deploying Stack {stack_name}", "gray")
        try:
            subprocess.run(
                ["cdk", "deploy", stack_name, "--require-approval", "never"],
                capture_output=True,
                text=True,
                check=True,
            )
        except Exception as e:
            printer.stop_spinner()
            printer.print(f"\r{e}", "red")
            exit()

        printer.stop_spinner()
        printer.print(f"\rStack {stack_name} Deployed", "green", 0, 1)


@forge.command()
@click.option(
    "--output-file",
    help="Name of the output file",
    default="diagram.png",
)
@click.option("-i", "--include", help="Comma-separated files to watch", default=None)
@click.option(
    "-e", "--exclude", help="Comma-separated files to not watch", default=None
)
def diagram(output_file, include, exclude):
    """
    Create a diagram of the project in png format

    This command creates a diagram of the project, including all the functions, triggers, and services.
    """
    printer.show_banner("Diagram")

    try:
        printer.start_spinner("Synthesizing CDK")
        with open(os.devnull, "w") as devnull:
            subprocess.run(
                ["cdk", "synth"], stdout=devnull, stderr=subprocess.STDOUT, check=True
            )

    except Exception as e:
        printer.print(str(e), "red", 1, 1)
        printer.stop_spinner()
        exit()

    functions = json.load(open("functions.json", "r"))
    if exclude:
        functions = [
            function for function in functions if function["name"] not in exclude
        ]

    if include:
        functions = [function for function in functions if function["name"] in include]

    printer.change_spinner_legend("Creating Diagram")

    if "." in output_file:
        output_file = output_file.split(".")[0]

    create_diagram(functions, output_file)

    printer.stop_spinner()
    printer.print(f"\rDiagram created in {output_file}.png", "gray", 0, 1)


AVAILABLE_TESTS = sorted(["unit", "integration", "coverage", "all"])


@forge.command()
@click.argument("test_type", type=click.Choice(AVAILABLE_TESTS))
def test(test_type):
    """
    Run the tests or coverage of the project
    """

    if test_type == "unit":
        subprocess.run(["pytest", "-k", "unit", "."], check=True)

    elif test_type == "integration":
        subprocess.run(["pytest", "-k", "integration", "."], check=True)

    elif test_type == "coverage":
        subprocess.run(
            ["coverage", "run", "-m", "pytest", "-k", "unit", "."], check=True
        )
        subprocess.run(["coverage", "report"], check=True)

    elif test_type == "all":
        subprocess.run(["pytest", "."], check=True)


@forge.command()
def output():
    """
    List the outputs of the stacks on AWS CloudFormation
    """

    def get_cdk_stacks():
        # Run the cdk list command to get the stack names
        result = subprocess.run(["cdk", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error running 'cdk list':", result.stderr)
            return []

        # Split the output into a list of stack names
        stack_names = result.stdout.strip().split("\n")
        stacks = []
        for stack_name in stack_names:
            if "(" in stack_name:
                stacks.append(stack_name.split("(")[1].split(")")[0].strip())
            else:
                stacks.append(stack_name)
        return stacks

    # Create a CloudFormation client
    client = boto3.client("cloudformation")

    stack_names = get_cdk_stacks()

    # Iterate over the provided stack names and print their outputs
    for stack_name in stack_names:
        try:
            response = client.describe_stacks(StackName=stack_name)
            stacks = response["Stacks"]

            for stack in stacks:

                if "Outputs" in stack:
                    printer.print(f"Stack Name: {stack['StackName']}", "rose", 1)
                    for output in stack["Outputs"]:
                        output_key = output.get("OutputKey", "N/A")
                        output_value = output.get("OutputValue", "N/A")
                        printer.print(f"{output_key}: {output_value}", "gray")

        except Exception:
            pass

    printer.br()


if __name__ == "__main__":
    forge()
