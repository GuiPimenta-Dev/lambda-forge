import jwt


def lambda_handler(event, context):

    token = event["headers"].get("authorization")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        effect = "allow"
        picture = decoded_token.get("picture")
        first_name = decoded_token.get("given_name")
        last_name = decoded_token.get("family_name")
        email = decoded_token.get("email")
        context = {"picture": picture, "first_name": first_name, "last_name": last_name, "email": email}

    except:
        effect = "deny"
        context = {}

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
