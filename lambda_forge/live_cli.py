import json
import os
import subprocess

import boto3

from lambda_forge.live_apigtw import LiveApiGtw
from lambda_forge.live_lambda import LiveLambda
from lambda_forge.live_s3 import LiveS3
from lambda_forge.live_sns import LiveSNS
from lambda_forge.live_sqs import LiveSQS
from lambda_forge.printer import Printer

printer = Printer()


def run_live(function_name, timeout, trigger):
    data = json.load(open("cdk.json", "r"))
    region = data["context"]["region"]
    account = data["context"]["account"]

    if not region:
        printer.print("Region Not Found", "red", 1, 1)
        exit()

    if not account:
        printer.print("Account Not Found", "red", 1, 1)
        exit()

    iot_client = boto3.client("iot", region_name=region)
    iot_endpoint = iot_client.describe_endpoint()["endpointAddress"]
    iot_endpoint = iot_endpoint.replace(".iot.", "-ats.iot.")

    try:
        os.environ["TRACK_FUNCTIONS"] = "true"
        with open(os.devnull, "w") as devnull:
            subprocess.run(["cdk", "synth"], stdout=devnull, stderr=subprocess.STDOUT, check=True)
    except Exception as e:
        printer.print(str(e), "red", 1, 1)
        exit()

    data = json.load(open("cdk.json", "r"))
    functions = data["context"]["functions"]

    function_names = [function["name"] for function in functions]
    if function_name not in function_names:
        printer.print(f"Function {function_name} Not Found", "red", 1, 1)
        exit()

    stub_name = f"{function_name}-Live"

    for function in functions:
        if function["name"] == function_name:

            printer.start_spinner(f"Creating Function {stub_name}")
            urlpath = function.get("endpoint", function["name"].lower())
            live_lambda = LiveLambda(
                function["name"],
                region,
                timeout,
                iot_endpoint,
                account,
                urlpath,
                printer,
            )
            function_arn = live_lambda.create_lambda()

            if trigger == "api_gateway":
                live_apigtw = LiveApiGtw(account, region, urlpath, printer)
                endpoint = live_apigtw.create_endpoint(function_arn, stub_name)
                printer.print(f"\rEndpoint URL: {endpoint}", "cyan")

            if trigger == "sns":
                live_sns = LiveSNS(region, printer)
                topic_arn = live_sns.subscribe(function_arn, stub_name)
                printer.print(f"\rTopic ARN: {topic_arn}", "cyan")

            if trigger == "sqs":
                live_sqs = LiveSQS(region, printer)
                queue_url = live_sqs.subscribe(function_arn, stub_name)
                printer.print(f"\rQueue URL: {queue_url}", "cyan")

            if trigger == "s3":
                live_s3 = LiveS3(region, printer)
                bucket_arn = live_s3.subscribe(function_arn, stub_name)
                printer.print(f"\rBucket ARN: {bucket_arn}", "cyan")

            printer.stop_spinner()
            current_dir = os.path.dirname(os.path.abspath(__file__))
            subprocess.run(
                [
                    "python",
                    current_dir + "/live_server.py",
                    function["name"],
                    function["path"],
                    iot_endpoint,
                    trigger,
                ]
            )
