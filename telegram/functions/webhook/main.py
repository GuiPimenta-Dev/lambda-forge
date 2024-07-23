import json

import sm_utils

from . import utils


def lambda_handler(event, context):
    body = json.loads(event["body"])
    message = body.get("message") or body.get("edited_message")
    text = message["text"]
    chat_id = message["from"]["id"]
    first_name = message["from"]["first_name"]
    last_name = message["from"]["last_name"]

    bot_token = sm_utils.get_secret("telegram")

    if "/ask" in text:
        text = text.replace("/ask", "").strip()
        utils.send_typing(chat_id, bot_token)
        response = utils.get_answer_to_question(text)
        utils.send_message(chat_id, response, bot_token)

    else:
        message = f"Hello {first_name} {last_name}! I'm a bot that can answer questions about Lambda Forge. To ask a question, type '/ask' followed by your question."
        utils.send_message(chat_id, message, bot_token)

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
