from aws_cdk import Duration
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam


class REST:
    def __init__(self, scope, context, api) -> None:
        self.context = context
        self.scope = scope
        self.api = api
        self.__authorizers = {}
        self.__default_authorizer = None

    def create_endpoint(self, method, path, function, public, authorizer=None):
        resource = self.__create_resource(path)
        authorizer = self.__get_authorizer(public, authorizer)

        resource.add_method(
            method,
            apigateway.LambdaIntegration(handler=function, proxy=True),
            authorizer=authorizer,
        )

    def create_authorizer(self, authorizer, name, default=False):
        if self.__authorizers.get(name) is not None:
            raise Exception(f"Authorizer {name} already set")

        if self.__default_authorizer is not None and default is True:
            raise Exception("Default authorizer already set")

        if default:
            self.__default_authorizer = name

        try:
            authorizer.add_environment(
                "API_ARN",
                f"arn:aws:execute-api:{self.context.region}:{self.context.account}:{self.api.rest_api_id}/*",
            )
            authorizer = apigateway.RequestAuthorizer(
                self.scope,
                id=f"{name}-Authorizer",
                handler=authorizer,
                identity_sources=[
                    apigateway.IdentitySource.context("identity.sourceIp")
                ],
                results_cache_ttl=Duration.seconds(0),
            )
        except:
            pass

        self.__authorizers[name] = authorizer

    def create_docs(
        self, endpoint, artifact, authorizer=None, public=False, stages=None
    ):

        if stages and self.context.stage not in stages:
            return

        s3_integration_role = iam.Role(
            self.scope,
            f"{endpoint.replace('/','').title()}-API-Gateway-S3",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            role_name=self.context.create_id(f"{endpoint.replace('/','').title()}-S3"),
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

        docs_resource = self.__create_resource(endpoint)

        if authorizer and authorizer not in self.__authorizers:
            raise Exception(f"Authorizer {authorizer} not found")

        authorizer = self.__get_authorizer(public, authorizer)

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

    def __create_resource(self, endpoint):
        resources = list(filter(None, endpoint.split("/")))
        resource = self.api.root.get_resource(
            resources[0]
        ) or self.api.root.add_resource(resources[0])
        for subresource in resources[1:]:
            resource = resource.get_resource(subresource) or resource.add_resource(
                subresource
            )
        return resource

    def __get_authorizer(self, public, authorizer):
        if public:
            authorizer = None
        else:
            authorizer_name = authorizer or self.__default_authorizer
            if not authorizer_name:
                raise ValueError(
                    "No default authorizer set and no authorizer provided."
                )

            authorizer = self.__authorizers.get(authorizer_name)
            if authorizer is None:
                raise ValueError(f"Authorizer '{authorizer_name}' not found.")

        return authorizer
