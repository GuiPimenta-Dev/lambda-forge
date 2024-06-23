import json
import os
import boto3


def lambda_handler(event, context):

    # Retrieve the connection ID from the event
    connection_id = event["connection_id"]

    # Create a client for the API Gateway Management API
    api_gateway_management_client = boto3.client(
        "apigatewaymanagementapi", endpoint_url=os.environ.get("POST_TO_CONNECTION_URL")
    )

    # Send the payload to the WebSocket
    api_gateway_management_client.post_to_connection(
        ConnectionId=connection_id, Data=json.dumps({"connection_id": connection_id}).encode("utf-8")
    )

    return {"statusCode": 200}