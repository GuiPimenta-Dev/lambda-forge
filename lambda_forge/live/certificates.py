import json
import os
import tempfile

import boto3
import requests
from botocore.exceptions import ClientError


class CertificateGenerator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.temp_dir = tempfile.mkdtemp()
        return cls._instance

    def __init__(self, region):
        self.iot_client = boto3.client("iot", region_name=region)

    def generate_certificate(self):
        response = self.iot_client.describe_endpoint()
        iot_endpoint = response["endpointAddress"]

        # Create keys and certificate
        response = self.iot_client.create_keys_and_certificate(setAsActive=True)
        certificate_pem = response["certificatePem"]
        private_key = response["keyPair"]["PrivateKey"]
        certificate_arn = response["certificateArn"]

        # Get CA certificate
        ca_pem = requests.get(
            f"https://www.amazontrust.com/repository/AmazonRootCA1.pem?iot_endpoint={iot_endpoint}"
        ).text

        # Define file paths within the temporary directory
        certificate_file_path = os.path.join(self.temp_dir, "certificate.pem")
        private_key_file_path = os.path.join(self.temp_dir, "private_key.pem")
        ca_file_path = os.path.join(self.temp_dir, "ca.pem")

        # Write certificate, private key, and CA certificate to files
        with open(certificate_file_path, "w") as cert_file:
            cert_file.write(certificate_pem)

        with open(private_key_file_path, "w") as private_key_file:
            private_key_file.write(private_key)

        with open(ca_file_path, "w") as ca_file:
            ca_file.write(ca_pem)

        # Define the policy name
        policy_name = "FullAccessPolicy"

        # Define the policy document
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "iot:*", "Resource": "*"}],
        }

        try:
            response = self.iot_client.create_policy(
                policyName=policy_name, policyDocument=json.dumps(policy_document)
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                pass
            else:
                raise e

        self.iot_client.attach_policy(policyName=policy_name, target=certificate_arn)

        return certificate_file_path, private_key_file_path, ca_file_path
