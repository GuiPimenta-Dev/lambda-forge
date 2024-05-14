import json
import boto3
import os
import subprocess
from threading import Thread
from tabulate import tabulate

from lambda_forge.live.live_lambda import LiveLambda


class Live:
    def __init__(self, printer, log_file) -> None:
        cdk = json.load(open("cdk.json", "r"))
        self.account = cdk["context"]["account"]
        self.region = cdk["context"]["region"]
        self.printer = printer
        self.log_file = log_file
        self.functions = {}

    def intro(self):
        self.printer.show_banner("Live Server")
        functions = []
        for function in self.functions:
            functions.append(
                {
                    "Name": function,
                    "Triggers": self.functions[function]["triggers"],
                }
            )
        if functions:
            self.print_report(functions)

    def create_lambda(self, name, path, timeout):
        iot_endpoint = self.__get_iot_endpoint()
        self.live_lambda = LiveLambda(name, self.region, timeout, iot_endpoint, self.account, self.printer)
        function_arn = self.live_lambda.create_lambda()
        self.functions[name] = {"arn": function_arn, "triggers": []}
        self.__run_server(name, path)

    def attach_trigger(self, function_name, trigger):
        self.functions[function_name]["triggers"].append(trigger)

    def __get_iot_endpoint(self):
        iot_client = boto3.client("iot", region_name=self.region)
        iot_endpoint = iot_client.describe_endpoint()["endpointAddress"]
        iot_endpoint = iot_endpoint.replace(".iot.", "-ats.iot.")
        return iot_endpoint

    def __run_server(self, function_name, function_path):
        iot_endpoint = self.__get_iot_endpoint()

        def target():
            current_dir = os.path.dirname(os.path.abspath(__file__))
            subprocess.Popen(
                [
                    "python",
                    os.path.join(current_dir, "live_server.py"),
                    function_name,
                    function_path,
                    iot_endpoint,
                    self.log_file,
                ]
            )

        thread = Thread(target=target)
        thread.start()

    def print_report(self, functions):
        def format_triggers(triggers):
            if not triggers:
                return "No Triggers"
            formatted_triggers = []
            for trigger in triggers:
                details = ", ".join([f"{key.title()}: {value}" for key, value in trigger.items()])
                formatted_triggers.append(details)
            return "\n\n".join(formatted_triggers)

        headers = ["Name", "Triggers"]
        data_to_display = [[func["Name"], format_triggers(func["Triggers"])] for func in functions]

        for data in data_to_display:
            formated_text = ""
            triggers = data[-1].split("\n\n")
            for trigger in triggers:
                if trigger == "No Triggers":
                    formated_text += trigger
                    continue
                service = trigger.split(",")[0].split(": ")[1]
                resource = trigger.split(",")[1].strip()
                formated_text += f"{service} -> {resource}\n\n"
            data[-1] = formated_text
        self.printer.print(
            tabulate(
                data_to_display,
                headers=headers,
                tablefmt="rounded_grid",
                colalign=("center", "center"),
                rowalign=["center", "center"],
            ),
            color="gray",
        )
