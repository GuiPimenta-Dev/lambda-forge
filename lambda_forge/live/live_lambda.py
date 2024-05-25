import json
import os
import shutil
import tempfile
import time
import uuid
import zipfile

import boto3

from lambda_forge.live.certificates import CertificateGenerator


class LiveLambda:
    def __init__(self, function_name, region, timeout, iot_endpoint, account, printer) -> None:
        self.function_name = function_name
        self.region = region
        self.timeout = timeout
        self.iot_endpoint = iot_endpoint
        self.account = account
        self.iam_client = boto3.client("iam", region_name=self.region)
        self.lambda_client = boto3.client("lambda", region_name=self.region)
        self.printer = printer

    def create_lambda(self):
        self.__delete_lambda(self.function_name)
        role = self.__create_role()
        zip_file_name = self.__zip_lambda()
        layer_arn = self.__create_layer()
        with open(zip_file_name, "rb") as zip_file:
            self.printer.change_spinner_legend(f"Deploying {self.function_name}")
            response = self.lambda_client.create_function(
                FunctionName=self.function_name,
                Description="Lambda Function for Live Development with AWS IoT Core",
                Runtime="python3.9",
                Role=role["Role"]["Arn"],
                Handler="main.lambda_handler",
                Code={"ZipFile": zip_file.read()},
                Publish=True,
                Timeout=900,
                Environment={
                    "Variables": {
                        "CLIENT_ID": self.function_name,
                        "ENDPOINT": self.iot_endpoint,
                        "TIMEOUT_SECONDS": str(self.timeout),
                    }
                },
                Layers=[layer_arn],
            )
            function_arn = response["FunctionArn"]
            return function_arn

    def __zip_lambda(self) -> str:
        cert, private, ca = self.__create_certificates()
        temp_dir = tempfile.mkdtemp()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        live = current_dir + "/main.py"
        files_to_copy = [live, cert, private, ca]

        for file_name in files_to_copy:
            shutil.copy(file_name, temp_dir)

        zip_file_name = f"{self.function_name}.zip"
        zip_file_path = os.path.join(temp_dir, zip_file_name)
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if ".zip" in file:
                        continue
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), temp_dir),
                    )

        return zip_file_path

    def __create_certificates(self):
        self.printer.change_spinner_legend("Creating Certificates")
        cert_generator = CertificateGenerator(self.region)
        cert, private, ca = cert_generator.generate_certificate()
        return cert, private, ca

    def __create_role(self):
        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"},
            ],
        }

        role_name = "Live-Lambda-Role"
        try:
            role = self.iam_client.get_role(RoleName=role_name)

        except:
            self.printer.change_spinner_legend("Creating Role")
            role = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
            )
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            )
            time.sleep(6)

        return role

    def __create_layer(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        layer_response = self.lambda_client.publish_layer_version(
            LayerName="awsiot-layer",
            Description="Layer containing AWS IoT dependencies",
            Content={"ZipFile": open(current_dir + "/awsiot.zip", "rb").read()},
            CompatibleRuntimes=["python3.9"],
        )
        layer_arn = layer_response["LayerVersionArn"]
        return layer_arn

    def __delete_lambda(self, stub_name):
        function_arn = f"arn:aws:lambda:{self.region}:{self.account}:function:{stub_name}"
        try:
            mappings = self.lambda_client.list_event_source_mappings(FunctionName=function_arn)
            for mapping in mappings["EventSourceMappings"]:
                self.lambda_client.delete_event_source_mapping(UUID=mapping["UUID"])

        except Exception as e:
            pass

        try:
            self.lambda_client.delete_function(FunctionName=function_arn)
        except Exception as e:
            pass
