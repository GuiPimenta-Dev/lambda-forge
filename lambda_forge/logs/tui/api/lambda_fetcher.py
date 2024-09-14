import boto3
import json
from typing import List, Optional


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


def list_lambda_functions( stack_name: str) -> List[str]:
    return get_lambda_functions_for_stack(stack_name)
