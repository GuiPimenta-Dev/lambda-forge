import random
from datetime import datetime

import boto3
import requests
import sm_utils


def send_typing(chat_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendChatAction"

    payload = {"chat_id": chat_id, "action": "typing"}

    requests.post(url, json=payload)


def get_answer_to_question(question):
    url = "https://hmabz24f3k.execute-api.us-east-2.amazonaws.com/prod/question"

    querystring = {"query": question}

    secret = sm_utils.get_secret("youtube-live-insights")
    headers = {"secret": secret}

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(f"Response from answering a question: {response.json()}")
    return response.json().get(
        "response", "I'm sorry, I don't know the answer to that question."
    )


def send_message(chat_id, text, bot_token):

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

    response = requests.post(url, json=payload)
    print(f"Response from sending a message: {response.json()}")


def save_item_to_dynamodb(table_name, item):
    item = {**item, "SK": datetime.now().isoformat()}
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    response = table.put_item(Item=item)
    print(f"Response from saving item to DynamoDB: {response}")


def get_random_question_example():
    questions = [
        "What is Lambda Forge?",
        "How can I install Lambda Forge?",
        "What are the main features of Lambda Forge?",
        "How do I create a new Lambda function using Lambda Forge?",
        "What is the structure of a Lambda function created by Lambda Forge?",
        "How do I create an authorizer with Lambda Forge?",
        "What is the structure of an authorizer created by Lambda Forge?",
        "How can I create a service class for SNS with Lambda Forge?",
        "How do I work with Lambda Layers in Lambda Forge?",
        "How can I start a live server with Lambda Forge?",
        "What does the live server feature do in Lambda Forge?",
        "How do I view live logs during a live development session in Lambda Forge?",
        "What is the purpose of the live trigger feature in Lambda Forge?",
        "How can I trigger AWS services using Lambda Forge?",
        "How does Lambda Forge support multi-stage environments?",
        "How can I generate automatic documentation with Lambda Forge?",
        "What types of documentation does Lambda Forge generate automatically?",
        "How can I generate an architecture diagram with Lambda Forge?",
        "What is the command to generate the architecture diagram in Lambda Forge?",
        "How can I contribute to Lambda Forge?",
        "What is the purpose of the forge function command?",
        "How do I use the forge authorizer command?",
        "What is the structure of a service created by the forge service command?",
        "How do I create a custom Lambda Layer with Lambda Forge?",
        "What are the benefits of using Lambda Forge for serverless development?",
        "How do I manage dependencies in Lambda Forge?",
        "Can Lambda Forge be used with other AWS services besides Lambda?",
        "How do I deploy a Lambda function using Lambda Forge?",
        "What is the purpose of the forge layer command?",
        "How do I install custom layers in my virtual environment using Lambda Forge?",
        "What is the forge live server command used for?",
        "How do I monitor logs in real time with Lambda Forge?",
        "What is the forge live logs command?",
        "How do I publish messages to AWS resources using Lambda Forge?",
        "What is the forge live trigger command used for?",
        "How does Lambda Forge help with testing Lambda functions?",
        "What environments does Lambda Forge support?",
        "How do I set up CI/CD pipelines with Lambda Forge?",
        "What is the forge diagram command?",
        "How do I update Lambda Forge to the latest version?",
        "Can I use Lambda Forge to generate documentation for my existing Lambda functions?",
        "How do I create a new project with Lambda Forge?",
        "What is the best way to organize my Lambda functions using Lambda Forge?",
        "How does Lambda Forge handle configuration management?",
        "What are the benefits of using the CLI tool FORGE?",
        "Can I use Lambda Forge with other cloud providers?",
        "How does Lambda Forge integrate with AWS CodePipeline?",
        "What is the role of config.py in Lambda Forge projects?",
        "How can I customize the directory structure created by Lambda Forge?",
        "What is Dependency Injection in the context of Lambda Forge?",
    ]
    return random.choice(questions)
