import json
import os
import subprocess
import time
import click

from InquirerPy import get_style, inquirer

from lambda_forge.printer import Printer

from . import LiveApiGtw, LiveSNS, LiveSQS, LiveS3, LiveEventBridge, Live

printer = Printer()


def run_live(log_file):
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
        printer.print("Project Not Found", "red", 1, 1)
        exit()

    try:
        printer.start_spinner("Synthesizing CDK")
        with open(os.devnull, "w") as devnull:
            subprocess.run(
                ["cdk", "synth"], stdout=devnull, stderr=subprocess.STDOUT, check=True
            )
            printer.stop_spinner()

    except Exception as e:
        printer.print(str(e), "red", 1, 1)
        exit()

    data = json.load(open("cdk.json", "r"))
    functions = data["context"]["functions"]
    synth_function_names = [function["name"] for function in functions]

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
        live.intro()

        printer.br()
        options = ["New Function", "Create Trigger", "Synth"]

        choice = inquirer.select(
            message="Select an option: ",
            style=style,
            choices=options,
        ).execute()

        if choice == "New Function":
            printer.br()

            function_name = inquirer.select(
                message="Select a function: ",
                style=style,
                choices=synth_function_names,
            ).execute()

            timeout = input("Enter timeout in seconds [30]: ")
            if not timeout:
                timeout = 30
            path = functions[synth_function_names.index(function_name)]["path"]
            printer.show_banner("Live Server")
            printer.start_spinner(
                f"Creating Lambda Function Live-{project}-{function_name}"
            )
            live.create_lambda(f"Live-{project}-{function_name}", path, timeout)
            printer.stop_spinner()

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

            data = json.load(open("cdk.json", "r"))
            functions = data["context"]["functions"]
            synth_function_names = [function["name"] for function in functions]

        if choice == "Create Trigger":
            printer.br()

            if live.functions:
                options = list(live.functions.keys())
            else:
                printer.print("No functions found", "red")
                time.sleep(1)
                continue

            selected_function = inquirer.select(
                message="Select a function: ",
                style=style,
                choices=options,
            ).execute()

            printer.br()

            options = sorted(["API Gateway", "SNS", "SQS", "S3", "Event Bridge"])
            choice = inquirer.select(
                message="Select a trigger: ",
                style=style,
                choices=options,
            ).execute()
            function_arn = live.functions[selected_function]["arn"]

            try:
                if choice == "API Gateway":
                    printer.show_banner("Live Server")
                    printer.start_spinner(f"Creating API Gateway Trigger")
                    live_apigtw = LiveApiGtw(account, region, printer, project)
                    trigger = live_apigtw.create_trigger(
                        function_arn, selected_function
                    )

                if choice == "SNS":
                    live_sns = LiveSNS(region, account, printer)
                    topic_name = click.prompt("SNS Topic Name", type=str)
                    topic_name = f"Live-{project}-{topic_name.title()}"
                    printer.show_banner("Live Server")
                    printer.start_spinner(f"Creating {topic_name} Topic")
                    topic_arn = live_sns.create_or_get_topic(topic_name)
                    trigger = live_sns.create_trigger(
                        function_arn, selected_function, topic_arn
                    )

                if choice == "SQS":
                    live_sqs = LiveSQS(region, printer)
                    queue_name = click.prompt("SQS Queue Name", type=str)
                    queue_name = f"Live-{project}-{queue_name.title()}"
                    printer.show_banner("Live Server")
                    printer.start_spinner(f"Creating {queue_name} Queue")
                    queue_url, queue_arn = live_sqs.create_queue(queue_name)
                    trigger = live_sqs.subscribe(function_arn, queue_url, queue_arn)

                if choice == "S3":
                    live_s3 = LiveS3(region, printer)
                    bucket_name = click.prompt("S3 Bucket Name", type=str)
                    bucket_name = f"live-{project.lower()}-{bucket_name.lower()}"
                    printer.show_banner("Live Server")
                    printer.start_spinner(f"Creating {bucket_name} Bucket")
                    live_s3.create_bucket(bucket_name)
                    trigger = live_s3.subscribe(function_arn, account, bucket_name)

                if choice == "Event Bridge":
                    live_event = LiveEventBridge(region, printer)
                    bus_name = click.prompt("Event Bridge Bus Name", type=str)
                    bus_name = f"Live-{project}-{bus_name.title()}"
                    printer.show_banner("Live Server")
                    printer.start_spinner(f"Creating {bus_name} Bus")
                    live_event.create_bus(bus_name)
                    trigger = live_event.subscribe(function_arn, account, bus_name)

                live.attach_trigger(selected_function, trigger)
                printer.stop_spinner()

            except Exception as e:
                printer.stop_spinner()
                printer.print(str(e), "red", 1)
                time.sleep(7)
                continue
