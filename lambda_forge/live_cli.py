import json
import os
import subprocess

import boto3
from lambda_forge.logs import Logger
from lambda_forge.stub import Stub


logger = Logger()

data = json.load(open("cdk.json", "r"))
region = data["context"]["region"]
account = data["context"]["account"]

def run_live(function_name, timeout):

    iot_client = boto3.client("iot", region_name=region)

    iot_endpoint = iot_client.describe_endpoint()["endpointAddress"]
    iot_endpoint = iot_endpoint.replace(".iot.", "-ats.iot.")

    with open(os.devnull, "w") as devnull:
        subprocess.run(["cdk", "synth"], stdout=devnull, stderr=subprocess.STDOUT)
    
    data = json.load(open("cdk.json", "r"))
    functions = data["context"]["functions"]

    function_names = [function["name"] for function in functions]
    if function_name not in function_names:
        logger.log(f"Function {function_name} Not Found", "red", 1, 1)
        exit()

    stub_name = f"{function_name}-Live"

    for function in functions:
        if function["name"] == function_name:
            urlpath = function.get("endpoint", function["name"].lower())            
            stub = Stub(function["name"], region, timeout, iot_endpoint, account, urlpath)
            stub.delete_api_gateway_resources(stub_name)
            stub_url = stub.create_stub()
         
            logger.log(f"\rEndpoint URL: {stub_url}", "cyan")

            current_dir = os.path.dirname(os.path.abspath(__file__))
            subprocess.run(
                [
                    "python",
                    current_dir + "/live_server.py",
                    function["name"],
                    function["path"],
                    iot_endpoint,
                ]
            )
