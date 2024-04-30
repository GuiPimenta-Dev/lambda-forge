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
from lambda_forge.logs import Logger

logger = Logger()

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("function_name", type=str)
parser.add_argument("file_path", type=str)
parser.add_argument("iot_endpoint", type=str)

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
mqtt_client.connect()

logger.log(f"Connection Established", "white", 1, 1)


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
    event.pop("multiValueHeaders", None)
    event.pop("resource", None)
    event.pop("path", None)
    event.pop("multiValueQueryStringParameters", None)
    event.pop("stageVariables", None)
    event.pop("requestContext", None)
    event.pop("isBase64Encoded", None)
    keys_to_remove = [
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "cache-control",
        "CloudFront-Forwarded-Proto",
        "CloudFront-Is-Desktop-Viewer",
        "CloudFront-Is-Mobile-Viewer",
        "CloudFront-Is-SmartTV-Viewer",
        "CloudFront-Is-Tablet-Viewer",
        "CloudFront-Viewer-ASN",
        "CloudFront-Viewer-Country",
        "Host",
        "priority",
        "sec-ch-ua",
        "sec-ch-ua-mobile",
        "sec-ch-ua-platform",
        "sec-fetch-dest",
        "sec-fetch-mode",
        "sec-fetch-site",
        "sec-fetch-user",
        "upgrade-insecure-requests",
        "User-Agent",
        "Via",
        "X-Amz-Cf-Id",
        "X-Amzn-Trace-Id",
        "X-Forwarded-For",
        "X-Forwarded-Port",
        "X-Forwarded-Proto",
    ]
    filtered_headers = {key: value for key, value in event["headers"].items() if key not in keys_to_remove}
    event["headers"] = filtered_headers or None
    logger.log(f"Request: ", "green", 2, 1)
    logger.log(f"{json.dumps(event, indent=4)}", "green")


def log_response(response):
    logger.log(f"Response: ", "yellow", 1, 1)
    logger.log(f"{json.dumps(response, indent=4)}", "yellow", 0, 2)


watchdog_thread = threading.Thread(target=watchdog)
watchdog_thread.daemon = True
watchdog_thread.start()


while True:
    pass
