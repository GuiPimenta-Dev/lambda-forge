import base64
import json
import os
import pickle
import time

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


def lambda_handler(event, context):
    CLIENT_ID = os.environ.get("CLIENT_ID")
    ENDPOINT = os.environ.get("ENDPOINT")
    TIMEOUT = float(os.environ.get("TIMEOUT_SECONDS"))
    PORT = 443

    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
    mqtt_client.configureEndpoint(ENDPOINT, PORT)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ca = current_dir + "/ca.pem"
    private_key = current_dir + "/private_key.pem"
    certificate = current_dir + "/certificate.pem"
    mqtt_client.configureCredentials(ca, private_key, certificate)
    mqtt_client.connect()

    global response
    response = None

    def callback(client, userdata, message):
        global response
        response = message.payload.decode()
        try:
            mqtt_client.disconnect()
        except Exception as e:
            print(f"Unexpected error during disconnect: {e}")

    mqtt_client.subscribe(f"{CLIENT_ID}/response", 0, callback)

    payload = {"event": event, "context": context}
    payload_bytes = pickle.dumps(payload)
    payload_base64 = base64.b64encode(payload_bytes).decode("utf-8")
    mqtt_client.publish(f"{CLIENT_ID}/request", payload_base64, 0)

    start_time = time.time()
    while response is None and (time.time() - start_time) < TIMEOUT:
        time.sleep(0.1)

    if response is None:
        return {"statusCode": 408, "body": "Request Timeout"}

    return json.loads(response)
