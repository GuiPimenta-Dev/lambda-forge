import boto3
from typing import List, Optional
import json

from lambda_forge.logs.tui.api.log_watcher import ForgeError


def get_lambda_functions_for_stack(stack_name: str):
    # Create a CloudFormation client
    cf_client = boto3.client("cloudformation")

    # Create a Lambda client
    lambda_client = boto3.client("lambda")

    # Get the stack resources
    resources = cf_client.describe_stack_resources(StackName=stack_name)[
        "StackResources"
    ]

    # Filter out the Lambda function resources
    lambda_functions = []
    for resource in resources:
        if resource["ResourceType"] == "AWS::Lambda::Function":
            # Get the Lambda function details using the LogicalResourceId
            function_name = resource["PhysicalResourceId"]
            lambda_function = lambda_client.get_function(FunctionName=function_name)
            lambda_functions.append(lambda_function)

    return [f["Configuration"]["FunctionName"] for f in lambda_functions]

def get_all_lambda_functions():

    def load_project_name(config_file: str = "cdk.json") -> str:
        """Load the project name from the configuration file."""
        try:
            with open(config_file, "r") as cdk_file:
                return json.load(cdk_file)["context"]["name"]
        except IOError as e:
            raise ForgeError(f"Error loading project name from {config_file}: {e}")

    project_name = load_project_name()
    with open("functions.json", "r") as f:
        functions = json.load(f)

    return [project_name + "-" + f["name"] for f in functions]

def list_lambda_functions( stack_name: str) -> List[str]:
    if stack_name:
        return get_lambda_functions_for_stack(stack_name)
    else:
        return get_all_lambda_functions()
