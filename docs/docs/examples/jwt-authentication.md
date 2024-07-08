# Implementing a Serverless Authentication System with JWT, Dynamo DB, Secrets Manager and KMS

In this section, we will develop a serverless authentication system using JWT authentication. This system effectively transmits information from the client and authenticates users to gain access to endpoints containing private information.

JWT authentication is a secure method for transmitting information between parties as a JSON object. To gain a deeper understanding of JWT tokens and their functionality, you can refer to the article [JSON Web Tokens](http://127.0.0.1:8000/articles/page6/).

## Setting Up the DynamoDB Tables

To get started, we must create tables to store user credentials securely. For maximum decoupling of environments, proceed to your AWS console and create three separate tables, each designated for a specific stage: `Dev-Auth`, `Staging-Auth` and `Prod-Auth`.

Once you have obtained the ARNs for these tables, let's integrate them into the `cdk.json` file within the corresponding environment.

```python title="cdk.json" linenums="51" hl_lines="6 14 22"
   "dev": {
      "base_url": "https://api.lambda-forge.com/dev",
      "arns": {
        "urls_table": "$DEV-URLS-TABLE-ARN",
        "images_bucket": "$DEV-IMAGES-BUCKET-ARN",
        "auth_table": "$DEV-AUTH-TABLE-ARN"
      }
    },
    "staging": {
      "base_url": "https://api.lambda-forge.com/staging",
      "arns": {
        "urls_table": "$STAGING-URLS-TABLE-ARN",
        "images_bucket": "$STAGING-IMAGES-BUCKET-ARN",
        "auth_table": "$STAGING-AUTH-TABLE-ARN"
      }
    },
    "prod": {
      "base_url": "https://api.lambda-forge.com",
      "arns": {
        "urls_table": "$PROD-URLS-TABLE-ARN",
        "images_bucket": "$PROD-IMAGES-BUCKET-ARN",
        "auth_table": "$PROD-AUTH-TABLE-ARN"
      }
    }
```

Next, we'll create a new variable class within the DynamoDB class to reference our JWT tables.

```python title="infra/services/dynamo_db.py" hl_lines="10-14" linenums="8"
        self.urls_table = dynamo_db.Table.from_table_arn(
            scope,
            "URLsTable",
            context.resources["arns"]["urls_table"],
        )

        self.auth_table = dynamo_db.Table.from_table_arn(
            scope,
            "AuthTable",
            context.resources["arns"]["auth_table"],
        )
```

## Implementing Password Hashing with KMS

As we're dealing with sensitive data such as passwords, storing them in plain text poses a significant security risk. To mitigate this risk, we'll utilize KMS (Key Management Service), an AWS resource designed for hashing passwords and other sensitive information.

To create a new KMS service, execute the following command:

```
forge service kms
```

This command creates a new file within the `infra/services` directory specifically for managing KMS keys.

```hl_lines="7"
infra
└── services
    ├── __init__.py
    ├── api_gateway.py
    ├── aws_lambda.py
    ├── dynamo_db.py
    ├── kms.py
    ├── layers.py
    ├── s3.py
    └── secrets_manager.py
```

Next, navigate to your AWS KMS console on AWS and create a new key. Then, update the KMS class with the ARN of the newly generated key.

```python title="infra/services/kms.py" hl_lines="7-11"
from aws_cdk import aws_kms as kms


class KMS:
    def __init__(self, scope, context) -> None:

        self.auth_key = kms.Key.from_key_arn(
            scope,
            "AuthKey",
            key_arn="$AUTH-KEY-ARN",
        )
```

## Creating a JWT Secret on Secrets Manager

To validate JWT tokens securely, a secret is essential. This secret, usually a random string, acts as a key for verifying whether the token was generated from a trusted source. It ensures that only authorized parties can generate and verify tokens, preventing unauthorized access to protected resources.

By storing the secret securely, you safeguard the integrity and confidentiality of your authentication system, mitigating the risk of unauthorized access and data breaches. Having that said, navigate to AWS Secrets Manager, create a new secret and save your random string there.

After obtaining the secret ARN from AWS Secrets Manager, integrate it into the Secrets Manager class.

```python title="infra/services/secrets_manager.py" linenums="4" hl_lines="10-14"
class SecretsManager:
    def __init__(self, scope, resources) -> None:

        self.gmail_secret = secrets_manager.Secret.from_secret_complete_arn(
            scope,
            id="GmailSecret",
            secret_complete_arn="$GMAIL-SECRET-ARN",
        )

        self.jwt_secret = secrets_manager.Secret.from_secret_complete_arn(
            scope,
            id="JwtSecret",
            secret_complete_arn="$JWT-SECRET-ARN",
        )
```

## Using the PYJWT Public Layer

To hash our JWT tokens, we'll leverage the widely-used Python library called `pyjwt`. Due to its popularity, AWS conveniently offers it as a public layer, streamlining our authentication implementation.

- PYJWT: `arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p39-PyJWT:3`

Let's now create a new class variable refencing the pyjwt layer.

```python title="infra/services/layers.py" hl_lines="9-13" linenums="14"
        self.sm_utils_layer = _lambda.LayerVersion(
            scope,
            id='SmUtilsLayer',
            code=_lambda.Code.from_asset(Path.layer('layers/sm_utils')),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='',
         )

        self.pyjwt_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="JWTLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p39-PyJWT:3",
        )
```

Don't forget to add the pyjwt layer in the `requirements.txt`

```title="requirements.txt" linenums="15"
jwt==1.3.1
```

## Implementing the SignUp Function

Now that we have all the necessary components set up, it's time to develop our authentication logic. We'll begin with the signup function, which is responsible for receiving an email and a password from the user. This function will then store them in the database, ensuring that the user is unique and storing a hashed version of the password for security purposes.

```
forge function signup --method "POST" --description "Securely handle user registration with unique credentials." --public --belongs-to auth --no-tests --endpoint signup
```

This command generates a new function within the `auth` directory.

```
functions
└── auth
    ├── signup
    │   ├── __init__.py
    │   ├── config.py
    │   ├── main.py
    └── utils
        └── __init__.py
```

The signup functionality can be implemented as follows:

```python title="functions/auth/signup/main.py"
import json
import os
from dataclasses import dataclass

import boto3


@dataclass
class Input:
    email: str
    password: int


@dataclass
class Output:
    pass


def encrypt_with_kms(plaintext: str, kms_key_id: str) -> str:
    kms_client = boto3.client("kms")
    response = kms_client.encrypt(KeyId=kms_key_id, Plaintext=plaintext.encode())
    return response["CiphertextBlob"]


def lambda_handler(event, context):
    # Retrieve the DynamoDB table name and KMS key ID from environment variables.
    AUTH_TABLE_NAME = os.environ.get("AUTH_TABLE_NAME")
    KMS_KEY_ID = os.environ.get("KMS_KEY_ID")

    # Initialize a DynamoDB resource.
    dynamodb = boto3.resource("dynamodb")

    # Reference the DynamoDB table.
    auth_table = dynamodb.Table(AUTH_TABLE_NAME)

    # Parse the request body to get user data.
    body = json.loads(event["body"])

    # Verify if the user already exists.
    user = auth_table.get_item(Key={"PK": body["email"]})
    if user.get("Item"):
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "User already exists"}),
        }

    # Encrypt the password using KMS.
    encrypted_password = encrypt_with_kms(body["password"], KMS_KEY_ID)

    # Insert the new user into the DynamoDB table.
    auth_table.put_item(Item={"PK": body["email"], "password": encrypted_password})

    # Return a successful response with the newly created user ID.
    return {"statusCode": 201}
```

This Lambda function basically handles user signup by encrypting passwords with KMS and storing them in DynamoDB, ensuring secure user registration.

With our implementation ready, let's configure it to utilize AWS resources for seamless functionality.

```python title="functions/auth/signup/config.py" hl_lines="12-15 20 22"
from infra.services import Services


class SignUpConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="SignUp",
            path="./functions/auth",
            description="Securely handle user registration with unique credentials.",
            directory="signup",
            environment={
                "AUTH_TABLE_NAME": services.dynamo_db.auth_table.table_name,
                "KMS_KEY_ID": services.kms.auth_key.key_id,
            },
        )

        services.api_gateway.create_endpoint("POST", "/signup", function, public=True)

        services.dynamo_db.auth_table.grant_read_write_data(function)

        services.kms.auth_key.grant_encrypt(function)
```

## Implementing the SignIn Functionality

Now that the signup functionality is in place, let's proceed with the implementation of the signin function. This function will handle user input of email and password, verify them against existing credentials in the database, and decrypt the encrypted password to authenticate the user.

```
forge function signin --method "POST" --description "Authenticate user login by verifying email and password against stored credentials" --public --belongs-to auth --no-tests --endpoint signin
```

Here's our updated folder structure:

```
functions
└── auth
    ├── signin
    │   ├── __init__.py
    │   ├── config.py
    │   └── main.py
    ├── signup
    │   ├── __init__.py
    │   ├── config.py
    │   └── main.py
    └── utils
        └── __init__.py
```

And now, it's implementation.

```python title="functions/auth/signup/main.py" linenums="1"
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
```

Note that upon matching the input password with the encrypted password, the email is encoded within the JWT token and returned to the client, specifically on line 62. This step is crucial for facilitating retrieval of this information at a later stage.

Now, let's move on to configure the signin function.

```python title="functions/auth/signup/config.py" hl_lines="12-17 22 24 26"
from infra.services import Services


class SigninConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Signin",
            path="./functions/auth",
            description="Authenticate user login by verifying email and password against stored credentials",
            directory="signin",
            layers=[services.layers.sm_utils_layer, services.layers.pyjwt_layer],
            environment={
                "AUTH_TABLE_NAME": services.dynamo_db.auth_table.table_name,
                "KMS_KEY_ID": services.kms.auth_key.key_id,
                "JWT_SECRET_NAME": services.secrets_manager.jwt_secret.secret_name,
            },
        )

        services.api_gateway.create_endpoint("POST", "/signin", function, public=True)

        services.dynamo_db.auth_table.grant_read_data(function)

        services.kms.auth_key.grant_decrypt(function)

        services.secrets_manager.jwt_secret.grant_read(function)
```

## Creating the JWT Authorizer

Now that we have the signin function, it returns a token to the client, typically a frontend application, which must include this token in the headers of subsequent requests protected by the JWT authorizer. The authorizer's role is to decode if the token was generated with the same hash as its creation, and if so, decode the token and pass the email to the protected functions.

With that being said, let's proceed with its implementation.

```
forge authorizer jwt --description "A jwt authorizer for private lambda functions" --no-tests
```

This command creates a new `jwt` authorizer under the `authorizers` folder.

```
authorizers
  ├── jwt
  │   ├── __init__.py
  │   ├── config.py
  │   └── main.py
  └── utils
      └── __init__.py
```

Now, let's proceed with the implementation.

```python title="authorizers/jwt/main.py"
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
```

This function attempts to decode the token received in the headers under the key `authorization` using the same JWT secret stored in Secrets Manager that was used during its generation. If successful, it retrieves the hashed email from the signin function and passes it as context.

Now, let's set up our new JWT authorizer.

```python title="authorizers/jwt/config.py" hl_lines="11-14 17 19"
from infra.services import Services


class JwtAuthorizerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="JwtAuthorizer",
            path="./authorizers/jwt",
            description="A jwt authorizer for private lambda functions",
            layers=[services.layers.sm_utils_layer, services.layers.pyjwt_layer],
            environment={
                "JWT_SECRET_NAME": services.secrets_manager.jwt_secret.secret_name
            },
        )

        services.api_gateway.create_authorizer(function, name="jwt", default=False)

        services.secrets_manager.jwt_secret.grant_read(function)
```

## Creating a Private Function

Now it's time to create a simple private function that can only be acessible through requests that passes the validations made through the authorizer.

```
forge function hello --method "GET" --description "A private function" --no-tests
```

This command creates a standalone function in the root of the `functions` folder.

```
functions
└── hello
    ├── __init__.py
    ├── config.py
    └── main.py
```

Now, let's implement a very straightforward function that should simply retrieve the email decoded by the authorizer and return it to the user.

```python title="functions/hello/main.py"
import json
from dataclasses import dataclass


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    email = event["requestContext"]["authorizer"]["email"]

    return {"statusCode": 200, "body": json.dumps({"message": f"Hello, {email}!"})}
```

Finally, it's configuration.

```python title="functions/hello/config.py" hl_lines="13"
from infra.services import Services


class HelloConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Hello",
            path="./functions/hello",
            description="A private function",
        )

        services.api_gateway.create_endpoint("GET", "/hello", function, authorizer="jwt")
```

Note that because we didn't specify the JWT authorizer as default, and this function isn't marked as public, we need to explicitly pass the authorizer's name to the `create_endpoint` method.

## Deploying the Functions

Next, we'll commit our code and push it to GitHub, following these steps:

```bash
# Send your changes to stage
git add .

# Commit with a descriptive message
git commit -m "JWT Authentication System"

# Push changes to the 'dev' branch
git push origin dev

# Merge 'dev' into 'staging' and push
git checkout staging
git merge dev
git push origin staging

# Finally, merge 'staging' into 'main' and push
git checkout main
git merge staging
git push origin main
```

This sequence ensures our code passes through development, staging, and finally, production environments, activating our three distinct deployment pipelines.

![Pipelines running](images/three_example_pipelines.png)

After the pipelines complete, the Authentication system should be available across development, staging, and production stages.

## Testing the Functions

Let's start by testing the signup function with the credentials below:

- Email: `tutorial@lambda-forge.com`
- Password: `12345678`

```
curl --request POST \
  --url https://api.lambda-forge.com/signup \
  --header 'Content-Type: application/json' \
  --data '{
	"email": "tutorial@lambda-forge.com",
	"password": "12345678"
}'
```

The endpoint returns a status code `201`.

However, if we navigate to the `Prod-Auth` Table on the Dynamo DB console, we'll notice that the password stored isn't simply `12345678`, but rather a significantly lengthy hash string:

```
AQICAHinYrMBzzQKgEowcHc4llDo3C5gg+cRawehAsWTMZ24iwEvX3NrQs9oYi0hD2YnB28hAAAAZjBkBgkqhkiG9w0BBwagVzBVAgEAMFAGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMEeMCuyCVk4C+Nr4OAgEQgCOEKlx01+tGfqKTNXSktApuxUI31EnwzLt7GdW0wdXrT+Yu+A==
```

This showcases the robustness of the security measures in place to safeguard passwords.

Now, let's utilize the same credentials to log in:

```
curl --request POST \
  --url https://api.lambda-forge.com/signin \
  --header 'Content-Type: application/json' \
  --data '{
	"email": "tutorial@lambdaforge.com",
	"password": "12345678"
}'
```

The signin endpoint returns a token:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InR1dG9yaWFsQGxhbWJkYWZvcmdlLmNvbSJ9.ppQLiYZ-6AtHdwaCb-H-vJnjTCle9ppULqq5-TqVPjk"
}
```

Next, let's attempt a GET request to the hello function without headers:

```
curl --request GET \
  --url https://api.lambda-forge.com/hello
```

This returns the message:

```json
{
  "Message": "User is not authorized to access this resource with an explicit deny"
}
```

However, if we pass the token generated by the signin function:

```
curl --request GET \
  --url https://api.lambda-forge.com/hello \
  --header 'authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InR1dG9yaWFsQGxhbWJkYWZvcmdlLmNvbSJ9.ppQLiYZ-6AtHdwaCb-H-vJnjTCle9ppULqq5-TqVPjk'
```

We receive the desired output:

```json
{
  "message": "Hello, tutorial@lambda-forge.com!"
}
```

🎉 Congratulations! You've successfully implemented a JWT authentication system, securing your endpoints.🔒
