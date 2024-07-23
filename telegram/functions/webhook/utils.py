import requests
import sm_utils


def send_typing(chat_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendChatAction"

    payload = {"chat_id": chat_id, "action": "typing"}

    requests.post(url, json=payload)


def get_answer_to_question(question):
    url = "https://21r2uzrw97.execute-api.us-east-2.amazonaws.com/prod/question"

    querystring = {"query": question}

    secret = sm_utils.get_secret("youtube-live-insights")
    headers = {"secret": secret}

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(f"Response from answering a question: {response.json()}")
    return response.json().get("response", "I'm sorry, I don't know the answer to that question.")


def send_message(chat_id, text, bot_token):

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

    response = requests.post(url, json=payload)
    print(f"Response from sending a message: {response.json()}")
