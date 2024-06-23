import os

import jwt
import sm_utils


def lambda_handler(event, context):

    # Extract the JWT token from the event
    token = event["headers"].get("authorization")

    # Retrieve the JWT secret from Secrets Manager
    JWT_SECRET_NAME = os.environ.get("JWT_SECRET_NAME")
    JWT_SECRET = sm_utils.get_secret(JWT_SECRET_NAME)

    try:
        # Decode the JWT token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        effect = "allow"
        email = decoded_token.get("email")
    except:
        effect = "deny"
        email = None

    # Set the decoded email as context
    context = {"email": email}

    # Allow access with the user's email
    return {
        "context": context,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": event["methodArn"],
                }
            ],
        },
    }
