import json
import os
from dataclasses import dataclass

import sm_utils
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    query = event["queryStringParameters"]["query"]
    OPENAI_API_KEY = sm_utils.get_secret("OPEN_API_KEY")

    chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=query),
    ]

    res = chat(messages)

    return {
        "statusCode": 200,
        "body": json.dumps({"response": res.content}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
