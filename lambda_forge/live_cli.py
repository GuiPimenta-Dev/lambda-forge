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

def run_live(function_name, timeout, urlpath, recreate):

    lambda_client = boto3.client("lambda", region_name=region)
    iot_client = boto3.client("iot", region_name=region)

    iot_endpoint = iot_client.describe_endpoint()["endpointAddress"]
    iot_endpoint = iot_endpoint.replace(".iot.", "-ats.iot.")

    with open(os.devnull, "w") as devnull:
        subprocess.run(["cdk", "synth"], stdout=devnull, stderr=subprocess.STDOUT)
    
    data = json.load(open("cdk.json", "r"))
    functions = data["context"]["functions"]

    function_names = [function["name"].lower() for function in functions]
    if function_name.lower() not in function_names:
        logger.log(f"Function {function_name} Not Found", "red", 1, 1)
        exit()

    if recreate:
        lambda_client.delete_function(FunctionName=f'{function_name}-Live')
        logger.log(f"Function {function_name}-Live Deleted", "red", 1, 1)

    for function in functions:
        if function["name"].lower() == function_name.lower():
            try:
                stub = lambda_client.get_function(FunctionName=f"{function['name']}-Live")
                stub_url = stub["Configuration"]["Environment"]["Variables"]["API_URL"]
            except lambda_client.exceptions.ResourceNotFoundException:
                stub = Stub(function["name"], region, timeout, iot_endpoint, account, urlpath)
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
