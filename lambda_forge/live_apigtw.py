import boto3


class LiveApiGtw:
    def __init__(self, account, region, urlpath, logger) -> None:
        self.stage = "live"
        self.account = account
        self.region = region
        self.urlpath = urlpath.strip("/")
        self.logger = logger
        self.api_client = boto3.client("apigateway", region_name=self.region)
        self.lambda_client = boto3.client("lambda", region_name=self.region)
        self.root_id = self.__create_api()["id"]

    def __create_api(self):
        name = "Live-Server-REST"
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

    def create_endpoint(self, function_arn, stub_name):
        self.logger.change_spinner_legend("Creating API Gateway Endpoint")

        self.__delete_lambda_resources(function_arn)

        all_resources = self.api_client.get_resources(restApiId=self.root_id)["items"]
        parent_id = next((resource["id"] for resource in all_resources if resource["path"] == "/"), None)

        urlpaths = self.urlpath.split("/")
        current_path = ""

        for part in urlpaths:
            current_path += f"/{part}"
            existing_resource = next((resource for resource in all_resources if resource["path"] == current_path), None)

            if not existing_resource:
                resource = self.api_client.create_resource(restApiId=self.root_id, parentId=parent_id, pathPart=part)
                parent_id = resource["id"]
                all_resources.append({"id": resource["id"], "path": current_path})
            else:
                parent_id = existing_resource["id"]

        self.api_client.put_method(
            restApiId=self.root_id, resourceId=parent_id, httpMethod="ANY", authorizationType="NONE"
        )

        self.api_client.put_integration(
            restApiId=self.root_id,
            resourceId=parent_id,
            httpMethod="ANY",
            type="AWS_PROXY",
            integrationHttpMethod="POST",
            uri=f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{function_arn}/invocations",
        )

        self.api_client.create_deployment(restApiId=self.root_id, stageName=self.stage)

        self.lambda_client.add_permission(
            FunctionName=stub_name,
            StatementId=f"ApiGatewayAccess-{parent_id}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:{self.region}:{self.account}:{self.root_id}/*/*",
        )

        endpoint = self.__get_endpoint_url()
        return endpoint

    def __delete_lambda_resources(self, function_arn):

        resources = self.api_client.get_resources(restApiId=self.root_id)["items"]

        linked_resources = []
        for resource in resources:
            for method in resource.get("resourceMethods", {}).keys():
                integration = self.api_client.get_integration(
                    restApiId=self.root_id, resourceId=resource["id"], httpMethod=method
                )
                if integration.get("uri", "").endswith(f"functions/{function_arn}/invocations"):
                    linked_resources.append(resource)

        for resource in sorted(linked_resources, key=lambda x: x["path"].count("/"), reverse=True):
            try:
                self.api_client.delete_resource(restApiId=self.root_id, resourceId=resource["id"])
            except:
                pass

    def __get_endpoint_url(self):
        endpoint_url = f"https://{self.root_id}.execute-api.{self.region}.amazonaws.com/{self.stage}/{self.urlpath}"
        return endpoint_url
