import json
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge, SQS, SNS
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3


def create_diagram(json_input, output_file):
    with Diagram(name="", show=False, filename=output_file, outformat="png"):
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
                trigger_name = trigger["trigger"]
                if service == "eventbridge":
                    if trigger_name not in service_nodes["eventbridge"]:
                        service_nodes["eventbridge"][trigger_name] = Eventbridge(trigger_name)
                    trigger_node = service_nodes["eventbridge"][trigger_name]
                elif service == "api_gateway":
                    if trigger_name not in service_nodes["apigateway"]:
                        service_nodes["apigateway"][trigger_name] = APIGateway(trigger_name)
                    trigger_node = service_nodes["apigateway"][trigger_name]
                elif service == "sqs":
                    if trigger_name not in service_nodes["sqs"]:
                        service_nodes["sqs"][trigger_name] = SQS(trigger_name)
                    trigger_node = service_nodes["sqs"][trigger_name]
                elif service == "sns":
                    if trigger_name not in service_nodes["sns"]:
                        service_nodes["sns"][trigger_name] = SNS(trigger_name)
                    trigger_node = service_nodes["sns"][trigger_name]
                elif service == "s3":
                    if trigger_name not in service_nodes["s3"]:
                        service_nodes["s3"][trigger_name] = S3(trigger_name)
                    trigger_node = service_nodes["s3"][trigger_name]
                elif service == "dynamodb":
                    if trigger_name not in service_nodes["dynamodb"]:
                        service_nodes["dynamodb"][trigger_name] = Dynamodb(trigger_name)
                    trigger_node = service_nodes["dynamodb"][trigger_name]
                else:
                    continue

                trigger_node >> lambda_function

            for invocation in function["invocations"]:
                service = invocation["service"]
                resource_id = invocation["resource"]
                if service == "dynamodb":
                    if resource_id not in service_nodes["dynamodb"]:
                        service_nodes["dynamodb"][resource_id] = Dynamodb(resource_id)
                    invocation_node = service_nodes["dynamodb"][resource_id]
                elif service == "s3":
                    if resource_id not in service_nodes["s3"]:
                        service_nodes["s3"][resource_id] = S3(resource_id)
                    invocation_node = service_nodes["s3"][resource_id]
                elif service == "sqs":
                    if resource_id not in service_nodes["sqs"]:
                        service_nodes["sqs"][resource_id] = SQS(resource_id)
                    invocation_node = service_nodes["sqs"][resource_id]
                elif service == "sns":
                    if resource_id not in service_nodes["sns"]:
                        service_nodes["sns"][resource_id] = SNS(resource_id)
                    invocation_node = service_nodes["sns"][resource_id]
                else:
                    continue

                lambda_function >> invocation_node