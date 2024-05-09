import boto3
import json

class LiveIAM:
    def __init__(self, region):
        self.iam_client = boto3.client('iam', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)

    def attach_policy_to_lambda(self, policy, function_arn):
        response = self.lambda_client.get_function(FunctionName=function_arn)
        role_arn = response['Configuration']['Role']
        role_name = role_arn.split('/')[-1]

        policy_name = "Live-SQS"

        try:
            policies = self.iam_client.list_policies(Scope='Local')
            for policy in policies['Policies']:
                if policy['PolicyName'] == policy_name:
                    policy_arn = policy['Arn']
                    break
        except Exception as e:
            print(f"Error listing policies: {e}")
        
        if policy_arn is None:
            try:
                policy_response = self.iam_client.create_policy(
                    PolicyName=policy_name,
                    PolicyDocument=json.dumps(policy)
                )
                policy_arn = policy_response['Policy']['Arn']
            except self.iam_client.exceptions.EntityAlreadyExistsException:
                print("Policy already exists, fetching the existing ARN.")
                policy_arn = [p['Arn'] for p in self.iam_client.list_policies()['Policies']
                                if p['PolicyName'] == policy_name][0]

        self.iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )