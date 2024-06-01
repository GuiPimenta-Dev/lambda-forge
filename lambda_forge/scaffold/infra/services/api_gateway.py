from aws_cdk import aws_apigateway as apigateway

from lambda_forge.services import REST


class APIGateway(REST):
    def __init__(self, scope, context):

        api = apigateway.RestApi(
            scope,
            id=context.gen_id("REST"),
            deploy_options={"stage_name": context.stage.lower()},
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            binary_media_types=["multipart/form-data"],
            default_cors_preflight_options={
                "allow_origins": ["*"],
                "allow_methods": apigateway.Cors.ALL_METHODS,
                "allow_credentials": True,
            },
        )

        super().__init__(scope=scope, context=context, api=api)
