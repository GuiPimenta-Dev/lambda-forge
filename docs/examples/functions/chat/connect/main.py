import json
import os

import boto3


def lambda_handler(event, context):

    # Retrieve the connection ID from the request context
    connection_id = event["requestContext"]["connectionId"]

    # Create a client for the AWS Lambda service
    lambda_client = boto3.client("lambda")

    # Retrieve the ARN of the target Lambda function from the environment variables
    TARGET_FUNCTION_ARN = os.environ.get("TARGET_FUNCTION_ARN")

    # Define the payload to pass to the target Lambda function
    payload = {"connection_id": connection_id}

    # Invoke the target Lambda function asynchronously
    lambda_client.invoke(FunctionName=TARGET_FUNCTION_ARN, InvocationType="Event", Payload=json.dumps(payload))

    return {"statusCode": 200}
