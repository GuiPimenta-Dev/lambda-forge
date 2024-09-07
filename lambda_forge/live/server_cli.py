import json
import os
import subprocess
import time

from InquirerPy import get_style, inquirer
from lambda_forge.live.tui import launch_forge_tui

from lambda_forge.printer import Printer
from lambda_forge.live.tui.api.forge import ForgeAPI
from . import Live, LiveApiGtw, LiveEventBridge, LiveS3, LiveSNS, LiveSQS

printer = Printer()


def create_api_gateway_trigger(account, region, project, function_arn, selected_function, endpoint, method):
    live_apigtw = LiveApiGtw(account, region, printer, project, endpoint)
    trigger = live_apigtw.create_trigger(function_arn, selected_function, method)
    return trigger


def create_sns_trigger(account, region, function_arn, selected_function, topic_name):
    live_sns = LiveSNS(region, account, printer)
    topic_arn = live_sns.create_or_get_topic(topic_name)
    trigger = live_sns.create_trigger(function_arn, selected_function, topic_arn)
    return trigger


def create_sqs_trigger(region, function_arn, queue_name):
    live_sqs = LiveSQS(region, printer)
    printer.show_banner("Live Server")
    printer.start_spinner(f"Creating {queue_name} Queue")
    queue_url, queue_arn = live_sqs.create_queue(queue_name)
    trigger = live_sqs.subscribe(function_arn, queue_url, queue_arn)
    return trigger


def create_s3_trigger(region, account, function_arn, bucket_name):
    live_s3 = LiveS3(region, printer)
    live_s3.create_bucket(bucket_name)
    trigger = live_s3.subscribe(function_arn, account, bucket_name)
    return trigger


def create_event_bridge_trigger(region, account, function_arn, bus_name):
    live_event = LiveEventBridge(region, printer)
    live_event.create_bus(bus_name)
    trigger = live_event.subscribe(function_arn, account, bus_name)
    return trigger


def run_live(include=None, exclude=None):
    printer.show_banner("Live Development")

    data = json.load(open("cdk.json", "r"))
    region = data["context"]["region"]
    account = data["context"]["account"]
    project = data["context"]["name"]

    if not region:
        printer.print("Region Not Found", "red", 1, 1)
        exit()

    if not account:
        printer.print("Account Not Found", "red", 1, 1)
        exit()

    if not project:
        printer.print("Project Name Not Found", "red", 1, 1)
        exit()

    try:
        printer.start_spinner("Synthesizing CDK")
        with open(os.devnull, "w") as devnull:
            subprocess.run(["cdk", "synth"], stdout=devnull, stderr=subprocess.STDOUT, check=True)
            printer.stop_spinner()

    except Exception as e:
        printer.print(str(e), "red", 1, 1)
        printer.stop_spinner()
        exit()

    functions = json.load(open("functions.json", "r"))

    if exclude:
        functions = [function for function in functions if function["name"] not in exclude]

    if include:
        functions = [function for function in functions if function["name"] in include]

    live = Live(printer, "live.log")

    server_functions = []
    for function in functions:
        try:
            function_name = f"Live-{project}-{function['name']}"
            printer.start_spinner(f"Creating Lambda Function {function_name}")
            live.create_lambda(function_name, function["path"], function["timeout"])
            time.sleep(4)
            for function_trigger in function["triggers"]:

                function_arn = f"arn:aws:lambda:{region}:{account}:function:{function_name}"

                if function_trigger["service"] == "api_gateway":
                    
                    trigger = create_api_gateway_trigger(
                        account,
                        region,
                        project,
                        function_arn,
                        function_name,
                        function_trigger["trigger"],
                        function_trigger["method"],
                    )
                    server_function = {
                        "service": "Api Gateway",
                        "name": function_name,
                        "type": "URL",
                        "trigger": trigger
                    }
                    server_functions.append(server_function)

                if function_trigger["service"] == "sns":
                    topic = f"Live-{project}-{function_trigger['trigger']}"
                    trigger = create_sns_trigger(account, region, function_arn, function_name, topic)
                    server_function = {
                        "service": "SNS",
                        "name": function_name,
                        "type": "Topic ARN",
                        "trigger": trigger
                    }
                    server_functions.append(server_function)

                if function_trigger["service"] == "sqs":
                    queue = f"Live-{project}-{function_trigger['trigger']}"
                    trigger = create_sqs_trigger(region, function_arn, queue)
                    server_function = {
                        "service": "SQS",
                        "name": function_name,
                        "type": "Queue URL",
                        "trigger": trigger
                    }
                    server_functions.append(server_function)

                if function_trigger["service"] == "s3":
                    bucket = f"live-{project.lower()}-{function_trigger['trigger'].replace('_', '-').replace(' ', '-').lower()}"
                    trigger = create_s3_trigger(region, account, function_arn, bucket)
                    server_function = {
                        "service": "S3",
                        "name": function_name,
                        "type": "Bucket Name",
                        "trigger": trigger
                    }
                    server_functions.append(server_function)

                if function_trigger["service"] == "event_bridge":
                    bus = f"Live-{project}-{function_trigger['trigger']}"
                    trigger = create_event_bridge_trigger(region, account, function_arn, bus)
                    server_function = {
                        "service": "Event Bridge",
                        "name": function_name,
                        "type": "Bus Name",
                        "trigger": trigger
                    }
                    server_functions.append(server_function)

                live.attach_trigger(function_name, trigger)

            printer.stop_spinner()

        except Exception as e:
            printer.print(str(e), "red", 1, 1)
            printer.stop_spinner()
            exit()
    
    ForgeAPI().set_functions(server_functions)
    launch_forge_tui()
