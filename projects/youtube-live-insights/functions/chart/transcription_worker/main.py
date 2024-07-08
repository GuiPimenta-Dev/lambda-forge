import json
import os

import boto3
import sm_utils
from openai import OpenAI


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")

    body = json.loads(event["Records"][0]["body"])

    s3 = boto3.client("s3")
    s3_bucket = body["s3_bucket"]
    s3_key = body["s3_key"]

    s3_object = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    payload = json.loads(s3_object["Body"].read().decode("utf-8"))

    video_id = payload["video_id"]
    chat = payload["messages"]
    label = payload["label"]
    interval = payload["interval"]
    index = payload["index"]
    min_messages = payload["min_messages"]
    author_summary = payload["prompt"]

    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME", "Dev-Result")

    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)

    messages = [message["message"] for message in chat]

    OPENAPI_KEY_SECRET_NAME = os.environ.get("OPENAPI_KEY_SECRET_NAME", "OPEN_API_KEY")
    api_key = sm_utils.get_secret(OPENAPI_KEY_SECRET_NAME)
    client = OpenAI(api_key=api_key)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    prompt = open(f"{current_dir}/prompt.txt").read()

    items = {
        "author_summary": author_summary,
        "chat": messages,
    }

    full_prompt = f"""{prompt}

{json.dumps(items)}
"""

    if len(messages) < int(min_messages):
        response = {
            "rating": "0",
            "reason": "Minimum number of messages not reached.",
            "chat_summary": "N/A",
        }

    else:
        try:
            completion = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=1,
                max_tokens=4096,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None,
            )
            response = json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(e)
            response = {
                "rating": "0",
                "reason": "N/A",
                "chat_summary": "N/A",
            }

    print(f"PK: {video_id}#INTERVAL={interval} Rating: {response['rating']} Reason: {response['reason']}")

    transcriptions_table.put_item(
        Item={
            "PK": f"{video_id}#INTERVAL={interval}",
            "SK": label,
            "chat": chat,
            "messages": messages,
            "rating": response["rating"],
            "reason": response["reason"],
            "chat_summary": response["chat_summary"],
        }
    )
