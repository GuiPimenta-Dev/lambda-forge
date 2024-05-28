from b_aws_websocket_api.ws_api import WsApi

from lambda_forge.services import WSS


class Websockets(WSS):
    def __init__(self, scope, context) -> None:

        wss= WsApi(
            scope=self.scope,
            id=self.context.gen_id("WSS"),
            name=self.context.gen_id("WSS"),
            route_selection_expression="$request.body.action",
        )
        
        super().__init__(scope=scope, context=context, wss=wss)
