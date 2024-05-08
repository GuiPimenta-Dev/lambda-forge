import json
import os
import subprocess

import boto3

from lambda_forge.live_apigtw import LiveApiGtw
from lambda_forge.live_lambda import LiveLambda
from lambda_forge.live_sns import LiveSNS
from lambda_forge.logs import Logger

logger = Logger()


def run_live(function_name, timeout, trigger):
    data = json.load(open("cdk.json", "r"))
    region = data["context"]["region"]
    account = data["context"]["account"]

    if not region:
        logger.log("Region Not Found", "red", 1, 1)
        exit()

    if not account:
        logger.log("Account Not Found", "red", 1, 1)
        exit()

    iot_client = boto3.client("iot", region_name=region)
    iot_endpoint = iot_client.describe_endpoint()["endpointAddress"]
    iot_endpoint = iot_endpoint.replace(".iot.", "-ats.iot.")

    try:
        subprocess.run(["export", "TRACK=true"], check=True)
        with open(os.devnull, "w") as devnull:
            subprocess.run(["cdk", "synth"], stdout=devnull, stderr=subprocess.STDOUT, check=True)
    except Exception as e:
        logger.log(str(e), "red", 1, 1)
        exit()

    data = json.load(open("cdk.json", "r"))
    functions = data["context"]["functions"]

    function_names = [function["name"] for function in functions]
    if function_name not in function_names:
        logger.log(f"Function {function_name} Not Found", "red", 1, 1)
        exit()

    stub_name = f"{function_name}-Live"

    for function in functions:
        if function["name"] == function_name:

            logger.start_spinner(f"Creating Function {stub_name}")
            urlpath = function.get("endpoint", function["name"].lower())
            live_lambda = LiveLambda(function["name"], region, timeout, iot_endpoint, account, urlpath, logger)
            function_arn = live_lambda.create_lambda()

            if trigger == "api_gateway":
                live_apigtw = LiveApiGtw(account, region, urlpath, logger)
                endpoint = live_apigtw.create_endpoint(function_arn, stub_name)
                logger.log(f"\rEndpoint URL: {endpoint}", "cyan")

            if trigger == "sns":
                live_sns = LiveSNS(region, logger)
                topic_arn = live_sns.subscribe(function_arn, stub_name)
                logger.log(f"\rTopic ARN: {topic_arn}", "cyan")

            logger.stop_spinner()
            current_dir = os.path.dirname(os.path.abspath(__file__))
            subprocess.run(
                ["python", current_dir + "/live_server.py", function["name"], function["path"], iot_endpoint, trigger]
            )
