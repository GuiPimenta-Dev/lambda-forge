import json
from base64 import b64encode

import boto3
import requests

with open("cdk.json", "r") as json_file:
    repo = json.load(json_file)["context"]["repo"]

REGION = "us-east-2"
SECRET_ARN = ""

session = boto3.session.Session()

client = session.client(service_name="secretsmanager", region_name=REGION)
SONAR_TOKEN = client.get_secret_value(SecretId=SECRET_ARN)["SecretString"]
TOKEN = b64encode(f"{SONAR_TOKEN}:".encode("utf-8")).decode("ascii")

url = "https://sonarcloud.io/api/project_pull_requests/list"
querystring = {"project": f"GuiPimenta-Dev_{repo}"}
headers = {"Authorization": f"Basic {TOKEN}"}

response = requests.request("GET", url, headers=headers, params=querystring)
if response.status_code == 404:
    raise Exception("Sonar Cloud is not configured")

pull_requests = response.json()["pullRequests"]
if len(pull_requests) > 0:
    pull_request_id = pull_requests[0]["key"]
    url = "https://sonarcloud.io/api/qualitygates/project_status"
    querystring = {
        "projectKey": f"GuiPimenta-Dev_{repo}",
        "organization": "GuiPimenta-Dev",
        "pullRequest": pull_request_id,
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    status = response.json()["projectStatus"]["status"]

    if status == "ERROR":
        raise Exception(f"Sonar Cloud failed: {response.json()}")
