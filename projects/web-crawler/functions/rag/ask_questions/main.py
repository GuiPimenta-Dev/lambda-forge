import json
import os

import boto3
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone

from . import utils


def get_secret(secret_name: str):
    sm_client = boto3.client("secretsmanager")
    response = sm_client.get_secret_value(SecretId=secret_name)

    try:
        secret = json.loads(response["SecretString"])

    except json.JSONDecodeError:
        secret = response["SecretString"]

    return secret


def lambda_handler(event, context):

    query = event["queryStringParameters"]["query"]

    PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "lambda-forge-telegram")
    PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
    OPENAI_API_KEY = get_secret("OPEN_API_KEY")
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    index = pinecone.Index(PINECONE_INDEX_NAME)
    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")

    prompt = utils.augment_prompt(index, embed_model, query)
    chat = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], model="gpt-3.5-turbo")

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=prompt),
    ]
    res = chat(messages)

    return {
        "statusCode": 200,
        "body": json.dumps({"response": res.content}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
