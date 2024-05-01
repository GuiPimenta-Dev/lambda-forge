import json
import os
import shutil
import time
import boto3
import tempfile
import zipfile
from lambda_forge.logs import Logger

from lambda_forge.certificates import CertificateGenerator


class Stub:
    def __init__(self, function_name, region, timeout, iot_endpoint, account, urlpath) -> None:
        self.function_name = function_name
        self.region = region
        self.timeout = timeout
        self.iot_endpoint = iot_endpoint
        self.account = account
        self.urlpath = urlpath.strip("/")
        self.api_client = boto3.client("apigateway", region_name=self.region)
        self.iam_client = boto3.client("iam", region_name=self.region)
        self.lambda_client = boto3.client("lambda", region_name=self.region)
        self.rest_api = self.__get_or_create_rest_api()
        self.logger = Logger()

    def create_stub(self):
        stub_name = f"{self.function_name}-Live"
        self.logger.start_spinner()
        self.logger.change_spinner_legend(f"Creating Function {stub_name}")
        role = self.__create_role()
        zip_file_name = self.__zip_lambda()
        layer_arn = self.__create_layer()
        endpoint_url = self.__get_endpoint_url()
        with open(zip_file_name, "rb") as zip_file:
            self.logger.change_spinner_legend("Deploying Lambda Function")
            response = self.lambda_client.create_function(
                FunctionName=stub_name,
                Description="Lambda Stub for Live Development with AWS IoT Core",
                Runtime="python3.9",
                Role=role["Role"]["Arn"],
                Handler="live.lambda_handler",
                Code={"ZipFile": zip_file.read()},
                Publish=True,
                Timeout=900,
                Environment={
                    "Variables": {
                        "CLIENT_ID": self.function_name,
                        "ENDPOINT": self.iot_endpoint,
                        "TIMEOUT_SECONDS": str(self.timeout),
                        "API_URL": endpoint_url,
                    }
                },
                Layers=[layer_arn],
            )
            function_arn = response["FunctionArn"]
            self.create_endpoint(function_arn, stub_name)
            self.logger.stop_spinner()
            return endpoint_url

    def __get_or_create_rest_api(self):
        name = "Live-REST"
        existing_apis = self.api_client.get_rest_apis()

        rest_api = None
        for api in existing_apis["items"]:
            if api["name"] == name:
                rest_api = api
                break

        if not rest_api:
            rest_api = self.api_client.create_rest_api(
                name=name, description="API Gateway for running Lambda Functions Live with AWS IoT"
            )
        return rest_api

    def __get_endpoint_url(self):
        root_id = self.rest_api["id"]
        endpoint_url = f"https://{root_id}.execute-api.{self.region}.amazonaws.com/live/{self.urlpath}"
        return endpoint_url

    def __zip_lambda(self) -> str:
        cert, private, ca = self.__create_certificates()
        temp_dir = tempfile.mkdtemp()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        live = current_dir + "/live.py"
        files_to_copy = [live, cert, private, ca]

        for file_name in files_to_copy:
            shutil.copy(file_name, temp_dir)

        zip_file_name = f"{self.function_name}.zip"
        zip_file_path = os.path.join(temp_dir, zip_file_name)
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), temp_dir),
                    )

        return zip_file_path

    def __create_certificates(self):
        self.logger.change_spinner_legend("Creating Certificates")
        cert_generator = CertificateGenerator()
        cert, private, ca = cert_generator.generate_certificate()
        return cert, private, ca

    def __create_role(self):
        assume_role_policy_document = assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"},
            ],
        }

        role_name = "Live-Lambda-Role"
        try:
            role = self.iam_client.get_role(RoleName=role_name)

        except:
            self.logger.change_spinner_legend("Creating Role")
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
        self.logger.change_spinner_legend("Creating Layer")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        layer_response = self.lambda_client.publish_layer_version(
            LayerName="awsiot-layer",
            Description="Layer containing AWS IoT dependencies",
            Content={"ZipFile": open(current_dir + "/resources/awsiot.zip", "rb").read()},
            CompatibleRuntimes=["python3.9"],
        )
        layer_arn = layer_response["LayerVersionArn"]
        return layer_arn

    def create_endpoint(self, function_arn, stub_name):
        self.logger.change_spinner_legend("Creating API Gateway Endpoint")
        root_id = self.rest_api["id"]

        all_resources = self.api_client.get_resources(restApiId=root_id)["items"]
        parent_id = next((resource["id"] for resource in all_resources if resource["path"] == "/"), None)

        urlpaths = self.urlpath.split("/")
        current_path = ""

        for part in urlpaths:
            current_path += f"/{part}"
            existing_resource = next((resource for resource in all_resources if resource["path"] == current_path), None)

            if not existing_resource:
                resource = self.api_client.create_resource(restApiId=root_id, parentId=parent_id, pathPart=part)
                parent_id = resource["id"]
                all_resources.append({"id": resource["id"], "path": current_path})
            else:
                parent_id = existing_resource["id"]

        self.api_client.put_method(restApiId=root_id, resourceId=parent_id, httpMethod="ANY", authorizationType="NONE")

        self.api_client.put_integration(
            restApiId=root_id,
            resourceId=parent_id,
            httpMethod="ANY",
            type="AWS_PROXY",
            integrationHttpMethod="POST",
            uri=f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{function_arn}/invocations",
        )

        # Deploy the API
        self.api_client.create_deployment(restApiId=root_id, stageName="live")

        # Set Lambda permissions
        self.lambda_client.add_permission(
            FunctionName=stub_name,
            StatementId=f"ApiGatewayAccess-{parent_id}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:{self.region}:{self.account}:{root_id}/*/*",
        )

    def delete_api_gateway_resources(self, function_name):
        root_id = self.rest_api["id"]
        try:
            function_arn = self.lambda_client.get_function(FunctionName=function_name)["Configuration"]["FunctionArn"]
        except self.lambda_client.exceptions.ResourceNotFoundException:
            return

        # Retrieve all resources
        resources = self.api_client.get_resources(restApiId=root_id)["items"]

        # Find all resources that are linked to the specific Lambda function
        linked_resources = []
        for resource in resources:
            for method in resource.get("resourceMethods", {}).keys():
                integration = self.api_client.get_integration(
                    restApiId=root_id, resourceId=resource["id"], httpMethod=method
                )
                if integration.get("uri", "").endswith(f"functions/{function_arn}/invocations"):
                    linked_resources.append(resource)

        # Delete resources linked to Lambda, deepest first
        for resource in sorted(linked_resources, key=lambda x: x["path"].count("/"), reverse=True):
            try:
                self.api_client.delete_resource(restApiId=root_id, resourceId=resource["id"])
            except Exception as e:
                pass
        # Optionally delete the Lambda function
        try:
            self.lambda_client.delete_function(FunctionName=function_name)
        except Exception as e:
            self.logger.log(f"Error: {e}", "red")
