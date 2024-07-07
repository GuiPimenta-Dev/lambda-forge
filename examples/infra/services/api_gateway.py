from aws_cdk import aws_apigateway as apigateway
from lambda_forge.api_gateway import REST
from lambda_forge.trackers import trigger


class APIGateway:
    def __init__(self, scope, context):

        self.api = apigateway.RestApi(
            scope,
            id=context.create_id("APIGateway"),
            deploy_options={"stage_name": context.stage.lower()},
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            binary_media_types=["multipart/form-data"],
            default_cors_preflight_options={
                "allow_origins": ["*"],
                "allow_methods": apigateway.Cors.ALL_METHODS,
                "allow_credentials": True,
            },
        )

        self.rest = REST(scope=scope, api=self.api, context=context)

    @trigger(service="api_gateway", trigger="path", function="function", extra=["method", "public"])
    def create_endpoint(self, method, path, function, public=False, authorizer=None):
        self.rest.create_endpoint(method=method, path=path, function=function, public=public, authorizer=authorizer)

    def create_authorizer(self, authorizer, name, default=False):
        self.rest.create_authorizer(authorizer=authorizer, name=name, default=default)

    def create_docs(self, endpoint, artifact, authorizer=None, public=False, stages=None):
        self.rest.create_docs(endpoint=endpoint, artifact=artifact, authorizer=authorizer, public=public, stages=stages)

    def create_cognito_integration(self, resource_path, handler, authorizer, method="ANY"):
        resource = self.api.root.add_resource(resource_path)
        resource.add_method(
            method,
            apigateway.LambdaIntegration(handler),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )
