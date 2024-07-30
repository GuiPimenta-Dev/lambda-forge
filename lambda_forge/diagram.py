from diagrams import Cluster, Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import SNS, SQS, Eventbridge
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3


def create_diagram(json_input, output_file):
    with Diagram(name="", show=False, filename=output_file, outformat="png"):
        folder_clusters = {}

        for function in json_input:
            function_name = function["name"]
            folder_path = "/".join(
                function["path"].split("/")[:-1]
            )  # Extract folder path

            if folder_path not in folder_clusters:
                folder_clusters[folder_path] = {}

            if "authorizer" in function["path"]:
                continue

            if function_name not in folder_clusters[folder_path]:
                folder_clusters[folder_path][function_name] = Lambda(function_name)

            lambda_function = folder_clusters[folder_path][function_name]

            for trigger in function["triggers"]:
                service = trigger["service"]
                trigger_name = trigger["trigger"]
                if service == "eventbridge":
                    if trigger_name not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][trigger_name] = Eventbridge(
                            trigger_name
                        )
                    trigger_node = folder_clusters[folder_path][trigger_name]
                elif service == "api_gateway":
                    trigger_name = f"{trigger['method'].upper()} {trigger_name}"
                    if trigger_name not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][trigger_name] = APIGateway(
                            trigger_name
                        )
                    trigger_node = folder_clusters[folder_path][trigger_name]
                elif service == "wss":
                    trigger_name = f"WSS {trigger_name}"
                    if trigger_name not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][trigger_name] = APIGateway(
                            trigger_name
                        )
                    trigger_node = folder_clusters[folder_path][trigger_name]
                elif service == "sqs":
                    if trigger_name not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][trigger_name] = SQS(trigger_name)
                    trigger_node = folder_clusters[folder_path][trigger_name]
                elif service == "sns":
                    if trigger_name not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][trigger_name] = SNS(trigger_name)
                    trigger_node = folder_clusters[folder_path][trigger_name]
                elif service == "s3":
                    if trigger_name not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][trigger_name] = S3(trigger_name)
                    trigger_node = folder_clusters[folder_path][trigger_name]
                elif service == "dynamodb":
                    if trigger_name not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][trigger_name] = Dynamodb(
                            trigger_name
                        )
                    trigger_node = folder_clusters[folder_path][trigger_name]
                else:
                    continue

                trigger_node >> lambda_function

            for invocation in function["invocations"]:
                service = invocation["service"]
                resource_id = invocation["resource"]
                if service == "dynamodb":
                    if resource_id not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][resource_id] = Dynamodb(
                            resource_id
                        )
                    invocation_node = folder_clusters[folder_path][resource_id]
                elif service == "s3":
                    if resource_id not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][resource_id] = S3(resource_id)
                    invocation_node = folder_clusters[folder_path][resource_id]
                elif service == "sqs":
                    if resource_id not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][resource_id] = SQS(resource_id)
                    invocation_node = folder_clusters[folder_path][resource_id]
                elif service == "sns":
                    if resource_id not in folder_clusters[folder_path]:
                        folder_clusters[folder_path][resource_id] = SNS(resource_id)
                    invocation_node = folder_clusters[folder_path][resource_id]
                else:
                    continue

                lambda_function >> invocation_node

        # Create clusters for each folder
        for folder, nodes in folder_clusters.items():
            with Cluster(folder):
                for node in nodes.values():
                    node
