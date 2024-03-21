from aws_cdk import Duration
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam


class APIGateway:
    def __init__(self, scope, context) -> None:
        self.endpoints = {}
        self.context = context
        self.scope = scope
        self.authorizers = {}
        self.default_authorizer = None
        self.api = apigateway.RestApi(
            scope,
            id=f"{self.context.stage}-{self.context.name}-API",
            description=f"{self.context.stage} {self.context.name} CDK API",
            deploy_options={"stage_name": self.context.stage.lower()},
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

    def create_endpoint(self, method, path, function, public=False, authorizer=None):
        resource = self.create_resource(path)
        if public:
            authorizer = None
        else:
            authorizer_name = authorizer or self.default_authorizer
            if not authorizer_name:
                raise ValueError(
                    "No default authorizer set and no authorizer provided."
                )

            authorizer = self.authorizers.get(authorizer_name)
            if authorizer is None:
                raise ValueError(f"Authorizer '{authorizer_name}' not found.")

        resource.add_method(
            method,
            apigateway.LambdaIntegration(handler=function, proxy=True),
            authorizer=authorizer,
        )

    def create_authorizer(self, function, name, default=False):
        if self.authorizers.get(name) is not None:
            raise Exception(f"Authorizer {name} already set")

        if self.default_authorizer is not None and default is True:
            raise Exception("Default authorizer already set")

        if default:
            self.default_authorizer = name

        function.add_environment(
            "API_ARN",
            f"arn:aws:execute-api:{self.context.region}:{self.context.account}:{self.api.rest_api_id}/*",
        )
        authorizer = apigateway.RequestAuthorizer(
            self.scope,
            id=f"{name}-Authorizer",
            handler=function,
            identity_sources=[apigateway.IdentitySource.context("identity.sourceIp")],
            results_cache_ttl=Duration.seconds(0),
        )

        self.authorizers[name] = authorizer

    def create_resource(self, endpoint):
        resources = list(filter(None, endpoint.split("/")))
        resource = self.api.root.get_resource(
            resources[0]
        ) or self.api.root.add_resource(resources[0])
        for subresource in resources[1:]:
            resource = resource.get_resource(subresource) or resource.add_resource(
                subresource
            )
        return resource

    def create_docs(self, authorizer):
        s3_integration_role = iam.Role(
            self.scope,
            "api-gateway-s3",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            role_name=f"{self.context.stage}-{self.context.name}-API-Gateway-S3-Integration-Role",
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

        if authorizer and authorizer not in self.authorizers:
            raise Exception(f"Authorizer {authorizer} not found")

        authorizer = self.authorizers[authorizer] if authorizer else None

        docs_resource.add_method(
            "GET",
            apigateway.AwsIntegration(
                service="s3",
                path=f"{self.context.bucket}/{self.context.name}/{self.context.stage.lower()}-swagger.html",
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
            authorizer=authorizer,
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
