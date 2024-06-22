import json
import os
import platform
import subprocess
import time

from InquirerPy import get_style, inquirer

from lambda_forge.printer import Printer

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


def run_live(log_file, input_file, output_file):
    printer.show_banner("Live Server")

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

    live = Live(printer, log_file)

    style = get_style(
        {
            "questionmark": "#25ABBE",
            "input": "#25ABBE",
            "pointer": "#25ABBE",
            "question": "#ffffff",
            "answered_question": "#25ABBE",
            "pointer": "#25ABBE",
            "answer": "white",
            "answermark": "#25ABBE",
        },
        style_override=True,
    )

    while True:

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

                    if function_trigger["service"] == "sns":
                        topic = f"Live-{project}-{function_trigger['trigger']}"
                        trigger = create_sns_trigger(account, region, function_arn, function_name, topic)

                    if function_trigger["service"] == "sqs":
                        queue = f"Live-{project}-{function_trigger['trigger']}"
                        trigger = create_sqs_trigger(region, function_arn, queue)

                    if function_trigger["service"] == "s3":
                        bucket = f"live-{project.lower()}-{function_trigger['trigger'].replace('_', '-').replace(' ', '-').lower()}"
                        trigger = create_s3_trigger(region, account, function_arn, bucket)

                    if function_trigger["service"] == "event_bridge":
                        bus = f"Live-{project}-{function_trigger['trigger']}"
                        trigger = create_event_bridge_trigger(region, account, function_arn, bus)

                    live.attach_trigger(function_name, trigger)

                printer.stop_spinner()

            except Exception as e:
                printer.print(str(e), "red", 1, 1)
                printer.stop_spinner()
                exit()

        live.intro()

        printer.br()
        options = ["Synth"]

        choice = inquirer.select(
            message="Select an option: ",
            style=style,
            choices=options,
        ).execute()

        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "live_server.py"], check=True)
        else:
            subprocess.run(["pkill", "-f", "live_server.py"], check=True)

        if choice == "Synth":
            printer.show_banner("Live Server")
            printer.start_spinner("Synthesizing CDK")
            with open(os.devnull, "w") as devnull:
                subprocess.run(
                    ["cdk", "synth"],
                    stdout=devnull,
                    stderr=subprocess.STDOUT,
                    check=True,
                )
                printer.stop_spinner()

            functions = json.load(open("functions.json", "r"))
