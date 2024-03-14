from aws_cdk import Duration
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk.aws_lambda import Code, Function, Runtime


class APIGateway:
    def __init__(self, scope, stage, arns) -> None:
        self.endpoints = {}
        self.stage = stage
        self.scope = scope
        self.arns = arns
        self.authorizers = {"default": None}
        name = scope.node.try_get_context("name")
        self.api = apigateway.RestApi(
            scope,
            id=f"{stage}-{name}-API",
            description=f"{stage} {name} CDK API",
            deploy_options={"stage_name": stage.lower()},
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            binary_media_types=["multipart/form-data"],
            minimum_compression_size=0,
            default_cors_preflight_options={
                "allow_origins": ["*"],
                "allow_headers": [
                    "Content-Type",
                    "applicationId",
                    "applicationid",
                    "Access-Control-Allow-Credentials",
                    "Access-Control-Allow-Origin",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                    "X-Amz-User-Agent",
                ],
                "allow_methods": apigateway.Cors.ALL_METHODS,
                "allow_credentials": True,
            },
        )

        self.__create_docs_endpoints(scope, name, stage)

    def create_endpoint(
        self, method, path, function, private=True, authorizer="default"
    ):
        if authorizer not in self.authorizers:
            raise Exception(f"Authorizer {authorizer} not found")

        resource = self.__create_resource(path)
        authorizer = self.authorizers[authorizer] if private else None
        resource.add_method(
            method,
            apigateway.LambdaIntegration(handler=function, proxy=True),
            authorizer=authorizer,
        )

        function_name = function._physical_name.split("-")[-1]
        self.endpoints[function_name] = {"method": method, "endpoint": path}

    def create_authorizer(self, function, name="default"):
        if self.authorizers.get(name) is not None:
            raise Exception(f"Authorizer {name} already set")

        function.add_environment(
            "API_ARN",
            f"arn:aws:execute-api:{self.scope.region}:{self.scope.account}:{self.api.rest_api_id}/*",
        )
        authorizer = apigateway.RequestAuthorizer(
            self.scope,
            id=f"{name}-Authorizer",
            handler=function,
            identity_sources=[apigateway.IdentitySource.context("identity.sourceIp")],
            results_cache_ttl=Duration.seconds(0),
        )

        self.authorizers[name] = authorizer

    def __create_resource(self, endpoint):
        resources = list(filter(None, endpoint.split("/")))
        resource = self.api.root.get_resource(resources[0])
        if not resource:
            resource = self.api.root.add_resource(resources[0])
        for subresource in resources[1:]:
            resource = resource.get_resource(subresource) or resource.add_resource(
                subresource
            )
        return resource

    def __create_docs_endpoints(self, scope, name, stage):
        docs_bucket_arn = self.arns["docs_bucket_arn"]
        s3_integration_role = iam.Role(
            scope,
            "api-gateway-s3",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            role_name=f"{stage}-{name}-API-Gateway-S3-Integration-Role",
        )

        s3_integration_role.add_to_policy(
            iam.PolicyStatement(
                resources=["*"],
                actions=[
                    "s3:Get*",
                    "s3:List*",
                    "s3-object-lambda:Get*",
                    "s3-object-lambda:List*",
                ],
            )
        )

        docs_resource = self.api.root.add_resource("docs")

        swagger_resource = docs_resource.add_resource("swagger")

        swagger_resource.add_method(
            "GET",
            apigateway.AwsIntegration(
                service="s3",
                path=f"{docs_bucket_arn}/{name}/{stage.lower()}-swagger.html",
                integration_http_method="GET",
                options=apigateway.IntegrationOptions(
                    credentials_role=s3_integration_role,
                    integration_responses=[
                        apigateway.IntegrationResponse(
                            status_code="200",
                        )
                    ],
                ),
            ),
            method_responses=[
                {
                    "statusCode": "200",
                    "responseModels": {
                        "text/html": apigateway.Model.EMPTY_MODEL,
                    },
                    "responseParameters": {
                        "method.response.header.Content-Type": True,
                    },
                }
            ],
        )
