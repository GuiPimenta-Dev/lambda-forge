from aws_cdk import aws_iam as iam
from aws_cdk.aws_lambda import CfnPermission
from b_aws_websocket_api.ws_api import WsApi
from b_aws_websocket_api.ws_deployment import WsDeployment
from b_aws_websocket_api.ws_lambda_integration import WsLambdaIntegration
from b_aws_websocket_api.ws_route import WsRoute
from b_aws_websocket_api.ws_stage import WsStage


class WSS:
    def __init__(self, scope, context, name, wss) -> None:
        self.scope = scope
        self.context = context
        self.name = name 
        self.websocket = wss

        self.stage = WsStage(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-WSS-Stage",
            ws_api=self.websocket,
            stage_name=context.stage.lower(),
            auto_deploy=True,
        )

        self.deployment = WsDeployment(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-Deploy",
            ws_stage=self.stage,
        )

        self.deployment.node.add_dependency(self.stage)

    def create_route(self, route_key, function):
        route_name = route_key.replace("$", "")

        CfnPermission(
            scope=self.scope,
            id=f"{function}-{self.name}-{route_name}-Invoke",
            action="lambda:InvokeFunction",
            function_name=function.function_name,
            principal="apigateway.amazonaws.com",
        )

        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["execute-api:ManageConnections"],
                resources=["*"],
            )
        )

        integration = WsLambdaIntegration(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-Integration-{route_name}",
            integration_name=f"{self.context.stage}-{self.name}-Integration-{route_name}",
            ws_api=self.websocket,
            function=function,
        )

        route = WsRoute(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-Route-{route_name}",
            ws_api=self.websocket,
            route_key=route_key,
            authorization_type="NONE",
            route_response_selection_expression="$default",
            target=f"integrations/{integration.ref}",
        )

        self.deployment.node.add_dependency(route)
