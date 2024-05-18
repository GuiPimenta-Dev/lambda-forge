import subprocess
import json
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge, SQS, SNS
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3


def create_diagram(json_input):
    with Diagram(name="", show=False, filename="diagram", outformat="png"):
        service_nodes = {
            "lambda": {},
            "dynamodb": {},
            "eventbridge": {},
            "apigateway": {},
            "sqs": {},
            "sns": {},
            "s3": {},
        }

        for function in json_input:
            function_name = function["name"]

            if function_name not in service_nodes["lambda"]:
                service_nodes["lambda"][function_name] = Lambda(function_name)

            lambda_function = service_nodes["lambda"][function_name]

            for trigger in function["triggers"]:
                service = trigger["service"]
                if service == "event_bridge":
                    trigger_name = trigger["trigger"]
                    if trigger_name not in service_nodes["eventbridge"]:
                        service_nodes["eventbridge"][trigger_name] = Eventbridge(trigger_name)
                    trigger_node = service_nodes["eventbridge"][trigger_name]
                elif service == "api_gateway":
                    trigger_name = trigger["trigger"]
                    if trigger_name not in service_nodes["apigateway"]:
                        service_nodes["apigateway"][trigger_name] = APIGateway(trigger_name)
                    trigger_node = service_nodes["apigateway"][trigger_name]
                elif service == "sqs":
                    trigger_name = trigger["trigger"]
                    if trigger_name not in service_nodes["sqs"]:
                        service_nodes["sqs"][trigger_name] = SQS(trigger_name)
                    trigger_node = service_nodes["sqs"][trigger_name]
                elif service == "sns":
                    trigger_name = trigger["trigger"]
                    if trigger_name not in service_nodes["sns"]:
                        service_nodes["sns"][trigger_name] = SNS(trigger_name)
                    trigger_node = service_nodes["sns"][trigger_name]
                elif service == "s3":
                    trigger_node = S3("S3")
                else:
                    continue

                trigger_node >> lambda_function

            for invocation in function["invocations"]:
                service = invocation["service"]
                if service == "dynamodb":
                    resource_id = invocation["resource_id"]
                    if resource_id not in service_nodes["dynamodb"]:
                        service_nodes["dynamodb"][resource_id] = Dynamodb(resource_id)
                    invocation_node = service_nodes["dynamodb"][resource_id]
                else:
                    continue

                lambda_function >> invocation_node


with open("functions.json", "r") as file:
    json_input = json.load(file)
create_diagram(json_input)

subprocess.run(["python", "embed_image_in_html.py", "diagram.png", "diagram.html"])
