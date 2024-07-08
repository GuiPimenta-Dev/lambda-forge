from b_aws_websocket_api.ws_api import WsApi
from lambda_forge.api_gateway import WSS
from lambda_forge.trackers import trigger


class Websockets:
    def __init__(self, scope, context) -> None:

        wss = WsApi(
            scope=scope,
            id=context.create_id("Websocket"),
            name=context.create_id("Websocket"),
            route_selection_expression="$request.body.action",
        )

        self.wss = WSS(scope=scope, context=context, wss=wss)

    @trigger(service="wss", trigger="route_key", function="function")
    def create_route(self, route_key, function):
        self.wss.create_route(route_key=route_key, function=function)
