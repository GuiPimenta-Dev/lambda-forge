import json
import os
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import uuid
import base64
import pickle
from lambda_forge.certificates import CertificateGenerator
import argparse
import importlib
import threading
from lambda_forge.live_apigtw import LiveApiGtw
from lambda_forge.live_sns import LiveSNS
from lambda_forge.logs import Logger

logger = Logger()

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("function_name", type=str)
parser.add_argument("file_path", type=str)
parser.add_argument("iot_endpoint", type=str)
parser.add_argument("trigger", type=str)

args = parser.parse_args()

main_file_path = args.file_path + "/main.py"

cert_generator = CertificateGenerator()
cert, private, ca = cert_generator.generate_certificate()

topic_request = f"{args.function_name}/request"
topic_response = f"{args.function_name}/response"
client_id = uuid.uuid4()
mqtt_client = AWSIoTMQTTClient(str(client_id))
mqtt_client.configureEndpoint(args.iot_endpoint, 443)
mqtt_client.configureCredentials(ca, private, cert)
try:
    mqtt_client.connect()
    logger.log(f"Connection Established", "white", 1)
except:
    logger.log(f"Connection Failed", "red", 1)
    exit()


def process(event, context):
    log_request(event)
    spec = importlib.util.spec_from_file_location("lambda_handler", main_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    response = module.lambda_handler(event, context)
    return response


def message_callback(client, userdata, message):

    decoded_bytes = base64.b64decode(message.payload)
    deserialized_data = pickle.loads(decoded_bytes)

    if message.topic == topic_request:
        response_payload = process(deserialized_data["event"], deserialized_data["context"])
        mqtt_client.publish(topic_response, json.dumps(response_payload), 0)
        log_response(response_payload)


mqtt_client.subscribe(topic_request, 1, message_callback)


def reload_lambda_handler():
    spec = importlib.util.spec_from_file_location("lambda_handler", main_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    globals()["lambda_handler"] = module.lambda_handler


def watchdog():
    last_modified = os.path.getmtime(main_file_path)
    while True:
        time.sleep(1)
        current_modified = os.path.getmtime(main_file_path)
        if current_modified != last_modified:
            reload_lambda_handler()
            last_modified = current_modified


def log_request(event):
    event = event.copy()
    if args.trigger == "api_gateway":
        event = LiveApiGtw.parse_logs(event)

    if args.trigger == "sns":
        event = LiveSNS.parse_logs(event)

    logger.log("------------------------ + ------------------------", "gray", 1)
    logger.log(f"Request: ", "white", 1, 1)
    logger.log(f"{json.dumps(event, indent=4)}", "white")


def log_response(response):
    logger.log(f"Response: ", "white", 1, 1)
    logger.log(f"{json.dumps(response, indent=4)}", "white")


watchdog_thread = threading.Thread(target=watchdog)
watchdog_thread.daemon = True
watchdog_thread.start()


while True:
    pass
