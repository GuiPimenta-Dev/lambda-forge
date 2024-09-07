import boto3


def list_lambda_functions():
    # Create a Lambda client
    client = boto3.client("lambda")

    # Initialize pagination
    paginator = client.get_paginator("list_functions")
    page_iterator = paginator.paginate()

    # Iterate through all pages and collect function names
    all_functions = []
    for page in page_iterator:
        functions = page["Functions"]
        for function in functions:
            all_functions.append(function["FunctionName"])

    return all_functions
