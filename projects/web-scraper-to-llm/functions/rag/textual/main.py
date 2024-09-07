import json
import os
from datetime import datetime

import sm_utils

from . import utils


def lambda_handler(event, context):


    body = json.loads(event["body"])
    message = body.get("message") or body.get("edited_message")
    text = message["text"]
    chat_id = message["from"]["id"]

    bot_token = sm_utils.get_secret("TEXTUAL-TELEGRAM-TOKEN")

    if "/ask" in text:
        text = text.replace("/ask", "").strip()
        utils.send_typing(chat_id, bot_token)
        response = utils.get_answer_to_question(text)
        utils.send_message(chat_id, response, bot_token)

    else:
        message = (
            "I'm powered by ChatGPT to assist you with any questions or issues you might have about Textual.\n\n"
            "Here is an example of what you can ask me: "
            f"`/ask $YOUR-QUESTION`\n\n"
        )

        utils.send_message(chat_id, message, bot_token)

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
