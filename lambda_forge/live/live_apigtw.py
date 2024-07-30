import boto3


class LiveApiGtw:
    def __init__(self, account, region, printer, project, endpoint) -> None:
        self.stage = "live"
        self.account = account
        self.region = region
        self.project = project
        self.printer = printer
        self.urlpath = endpoint.strip("/").lower()
        self.api_client = boto3.client("apigateway", region_name=self.region)
        self.lambda_client = boto3.client("lambda", region_name=self.region)
        self.root_id = self.__create_api()["id"]

    def __create_api(self):
        name = f"Live-{self.project}-REST"
        existing_apis = self.api_client.get_rest_apis()

        rest_api = None
        for api in existing_apis["items"]:
            if api["name"] == name:
                rest_api = api
                break

        if not rest_api:
            rest_api = self.api_client.create_rest_api(
                name=name,
                description="API Gateway for running Lambda Functions Live with AWS IoT",
            )
        return rest_api

    def create_trigger(self, function_arn, function_name, method):
        all_resources = self.api_client.get_resources(restApiId=self.root_id)["items"]
        parent_id = next(
            (resource["id"] for resource in all_resources if resource["path"] == "/"),
            None,
        )

        urlpaths = self.urlpath.split("/")
        current_path = ""

        for part in urlpaths:
            current_path += f"/{part}"
            existing_resource = next(
                (
                    resource
                    for resource in all_resources
                    if resource["path"] == current_path
                ),
                None,
            )

            if not existing_resource:
                resource = self.api_client.create_resource(
                    restApiId=self.root_id, parentId=parent_id, pathPart=part
                )
                parent_id = resource["id"]
                all_resources.append({"id": resource["id"], "path": current_path})
            else:
                parent_id = existing_resource["id"]

        try:
            response = self.api_client.get_method(
                restApiId=self.root_id, resourceId=parent_id, httpMethod=method
            )

            # If the method exists, delete it
            if response["httpMethod"] == method:
                self.api_client.delete_method(
                    restApiId=self.root_id, resourceId=parent_id, httpMethod=method
                )
        except:
            pass

        self.api_client.put_method(
            restApiId=self.root_id,
            resourceId=parent_id,
            httpMethod=method,
            authorizationType="NONE",
        )

        self.api_client.put_integration(
            restApiId=self.root_id,
            resourceId=parent_id,
            httpMethod=method,
            type="AWS_PROXY",
            integrationHttpMethod="POST",
            uri=f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{function_arn}/invocations",
        )

        self.api_client.create_deployment(restApiId=self.root_id, stageName=self.stage)

        try:
            self.lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f"ApiGatewayAccess-{parent_id}",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=f"arn:aws:execute-api:{self.region}:{self.account}:{self.root_id}/*/*",
            )
        except:
            pass

        endpoint = self.__get_endpoint_url()
        response = {"trigger": "API Gateway", "url": endpoint, "method": method}
        return response

    def __get_endpoint_url(self):
        endpoint_url = f"https://{self.root_id}.execute-api.{self.region}.amazonaws.com/{self.stage}/{self.urlpath}"
        return endpoint_url
