from aws_cdk import aws_apigateway as apigateway

from lambda_forge.trackers import track
from lambda_forge.api_gateway import REST


class APIGateway:
    def __init__(self, scope, context):

        api = apigateway.RestApi(
            scope,
            id=f"{context.stage}-{context.name}-API-Gateway",
            deploy_options={"stage_name": context.stage.lower()},
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            binary_media_types=["multipart/form-data"],
            default_cors_preflight_options={
                "allow_origins": ["*"],
                "allow_methods": apigateway.Cors.ALL_METHODS,
                "allow_credentials": True,
            },
        )

        self.rest = REST(scope=scope, context=context, api=api)

    @track
    def create_endpoint(self, method, path, function, public=None, authorizer=None):
        self.rest.create_endpoint(method=method, path=path, function=function, public=public, authorizer=authorizer)

    def create_authorizer(self, function, name, default=False):
        self.rest.create_authorizer(function=function, name=name, default=default)

    def create_docs(self, endpoint, artifact, authorizer=None, public=False, stages=None):
        self.rest.create_docs(endpoint=endpoint, artifact=artifact, authorizer=authorizer, public=public, stages=stages)
