import json
from datetime import datetime

import boto3


class LiveIAM:
    def __init__(self, region):
        self.iam_client = boto3.client("iam", region_name=region)
        self.lambda_client = boto3.client("lambda", region_name=region)

    def attach_policy_to_lambda(self, policy_dict, function_arn, policy_name):
        response = self.lambda_client.get_function(FunctionName=function_arn)
        role_arn = response["Configuration"]["Role"]
        role_name = role_arn.split("/")[-1]
        self.iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_dict),
        )
