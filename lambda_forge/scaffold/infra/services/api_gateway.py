from aws_cdk import Duration
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam
from lambda_forge import track
from lambda_forge.interfaces import IAPIGateway


class APIGateway(IAPIGateway):
    def __init__(self, scope, context) -> None:
        self.endpoints = {}
        self.context = context
        self.scope = scope
        self.authorizers = {}
        self.default_authorizer = None
        self.api = apigateway.RestApi(
            scope,
            id=f"{self.context.stage}-{self.context.name}-Rest",
            description=f"{self.context.stage} {self.context.name} Rest API",
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

    @track
    def create_endpoint(self, method, path, function, public=False, authorizer=None):
        resource = self.create_resource(path)
        authorizer = self.get_authorizer(public, authorizer)

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
        resource = self.api.root.get_resource(resources[0]) or self.api.root.add_resource(resources[0])
        for subresource in resources[1:]:
            resource = resource.get_resource(subresource) or resource.add_resource(subresource)
        return resource

    def create_docs(self, endpoint, artifact, authorizer=None, public=False, stages=None):

        if stages and self.context.stage not in stages:
            return

        s3_integration_role = iam.Role(
            self.scope,
            f"{endpoint.replace('/','').title()}-API-Gateway-S3",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            role_name=f"{self.context.stage}-{self.context.name}-{endpoint.replace('/','').title()}-S3",
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

        docs_resource = self.create_resource(endpoint)

        if authorizer and authorizer not in self.authorizers:
            raise Exception(f"Authorizer {authorizer} not found")

        authorizer = self.get_authorizer(public, authorizer)

        docs_resource.add_method(
            "GET",
            apigateway.AwsIntegration(
                service="s3",
                path=f"{self.context.bucket}/{self.context.name}/{self.context.stage.lower()}/{artifact.lower()}.html",
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

    def get_authorizer(self, public, authorizer):
        if public:
            authorizer = None
        else:
            authorizer_name = authorizer or self.default_authorizer
            if not authorizer_name:
                raise ValueError("No default authorizer set and no authorizer provided.")

            authorizer = self.authorizers.get(authorizer_name)
            if authorizer is None:
                raise ValueError(f"Authorizer '{authorizer_name}' not found.")

        return authorizer
