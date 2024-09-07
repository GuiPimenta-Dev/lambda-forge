def lambda_handler(event, context):

    # ATTENTION: The example provided below is strictly for demonstration purposes and should NOT be deployed in a production environment.
    # It's crucial to develop and integrate your own robust authorization mechanism tailored to your application's security requirements.
    # To utilize the example authorizer as a temporary placeholder, ensure to include the following header in your requests:

    # Header:
    # secret: CRMdDRMA4iW4xo9l38pACls7zsHYfp8T7TLXtucysb2lB5XBVFn8

    # Remember, security is paramount. This placeholder serves as a guide to help you understand the kind of information your custom authorizer should authenticate.
    # Please replace it with your secure, proprietary logic before going live. Happy coding!

    secret = event["headers"].get("secret")
    SECRET = "CRMdDRMA4iW4xo9l38pACls7zsHYfp8T7TLXtucysb2lB5XBVFn8"

    effect = "allow" if secret == SECRET else "deny"

    policy = {
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
    return policy
