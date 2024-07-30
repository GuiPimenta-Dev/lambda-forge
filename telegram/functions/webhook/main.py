import json
import os
from datetime import datetime

import sm_utils

from . import utils


def lambda_handler(event, context):

    MY_CHAT_ID = os.environ.get("MY_CHAT_ID")
    TELEGRAM_TABLE_NAME = os.environ.get("TELEGRAM_TABLE_NAME")

    body = json.loads(event["body"])
    message = body.get("message") or body.get("edited_message")
    text = message["text"]
    chat_id = message["from"]["id"]
    first_name = message["from"]["first_name"]
    last_name = message["from"]["last_name"]

    user_info = {
        "chat_id": chat_id,
        "first_name": first_name,
        "last_name": last_name,
        "message": text,
    }

    bot_token = sm_utils.get_secret("telegram")

    if "/ask" in text:
        text = text.replace("/ask", "").strip()
        utils.send_typing(chat_id, bot_token)
        response = utils.get_answer_to_question(text)
        utils.send_message(chat_id, response, bot_token)
        utils.save_item_to_dynamodb(
            TELEGRAM_TABLE_NAME, item={"PK": "ASK", **user_info, "response": response}
        )

    elif "/feedback" in text:
        text = text.replace("/feedback", "").strip()
        utils.save_item_to_dynamodb(
            TELEGRAM_TABLE_NAME, item={"PK": "FEEDBACK", **user_info}
        )
        utils.send_message(chat_id, "Thank you for your feedback!", bot_token)
        utils.send_message(
            MY_CHAT_ID,
            f"📝 Feedback from {first_name} {last_name}: \n\n{text}",
            bot_token,
        )

    elif "/feature" in text:
        text = text.replace("/feature", "").strip()
        utils.send_message(chat_id, "Thank you for your feature suggestion!", bot_token)
        utils.save_item_to_dynamodb(
            TELEGRAM_TABLE_NAME, item={"PK": "FEATURE", **user_info}
        )
        utils.send_message(
            MY_CHAT_ID,
            f"✨ Feature suggestion from {first_name} {last_name}: \n\n{text}",
            bot_token,
        )

    elif "/bug" in text:
        text = text.replace("/bug", "").strip()
        utils.send_message(chat_id, "Thank you for reporting the bug!", bot_token)
        utils.save_item_to_dynamodb(
            TELEGRAM_TABLE_NAME, item={"PK": "BUG", **user_info}
        )
        utils.send_message(
            MY_CHAT_ID,
            f"🐞 Bug report from {first_name} {last_name}: \n\n{text}",
            bot_token,
        )

    else:
        message = (
            f"Hello {first_name} {last_name}! 😊\n\n"
            "I'm powered by ChatGPT to assist you with any questions or issues you might have about Lambda Forge.\n\n"
            "Here is an example of what you can ask me: "
            f"`/ask {utils.get_random_question_example()}`\n\n"
            "/ask - To ask a question.\n"
            "/bug - To report a bug.\n"
            "/feature - To request a feature.\n"
            "/feedback - To provide some feedback.\n\n"
        )

        utils.send_message(chat_id, message, bot_token)

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
