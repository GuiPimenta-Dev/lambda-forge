from b_aws_websocket_api.ws_api import WsApi

from lambda_forge.websockets import WSS


class Websockets(WSS):
    def __init__(self, scope, context) -> None:
        super().__init__(scope=scope, context=context)

        self.websocket = WsApi(
            scope=self.scope,
            id=f"{self.context.stage}-{self.name}-WebSocket",
            name=f"{self.context.stage}-{self.name}-WebSocket",
            route_selection_expression="$request.body.action",
        )
