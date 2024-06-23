import json
import os
from dataclasses import dataclass

import boto3
import jwt
import sm_utils


@dataclass
class Input:
    email: str
    password: str


@dataclass
class Output:
    token: str


def decrypt_with_kms(ciphertext_blob: bytes, kms_key_id: str) -> str:
    kms_client = boto3.client("kms")

    # Then you can pass the decoded string to the decrypt method
    response = kms_client.decrypt(CiphertextBlob=bytes(ciphertext_blob), KeyId=kms_key_id)
    return response["Plaintext"].decode()


def lambda_handler(event, context):
    # Retrieve the DynamoDB table name and KMS key ID from environment variables.
    AUTH_TABLE_NAME = os.environ.get("AUTH_TABLE_NAME")
    KMS_KEY_ID = os.environ.get("KMS_KEY_ID")
    JWT_SECRET_NAME = os.environ.get("JWT_SECRET_NAME")

    JWT_SECRET = sm_utils.get_secret(JWT_SECRET_NAME)

    # Parse the request body to get user credentials.
    body = json.loads(event["body"])
    email = body["email"]
    password = body["password"]

    # Initialize a DynamoDB resource.
    dynamodb = boto3.resource("dynamodb")
    auth_table = dynamodb.Table(AUTH_TABLE_NAME)

    # Retrieve user data from DynamoDB.
    response = auth_table.get_item(Key={"PK": email})
    user = response.get("Item")

    # Check if user exists.
    if not user:
        return {"statusCode": 401, "body": json.dumps({"error": "User not found"})}

    # Check if user exists and password matches.
    encrypted_password = user.get("password")
    decrypted_password = decrypt_with_kms(encrypted_password, KMS_KEY_ID)

    # Compare the decrypted password with the provided one.
    if password == decrypted_password:
        # Generate JWT token
        status_code = 200
        token = jwt.encode({"email": email}, JWT_SECRET, algorithm="HS256")
        body = json.dumps({"token": token})

    else:
        status_code = 401
        body = json.dumps({"error": "Invalid credentials"})

    return {"statusCode": status_code, "body": body}
