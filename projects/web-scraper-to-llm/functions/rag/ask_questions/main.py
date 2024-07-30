import json
import os

import boto3
import sm_utils
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone

from . import utils


def lambda_handler(event, context):

    query = event["queryStringParameters"]["query"]
    index_name = event["queryStringParameters"].get(
        "index_name", "lambda-forge-telegram"
    )

    PINECONE_API_KEY = sm_utils.get_secret("PINECONE_API_KEY")
    OPENAI_API_KEY = sm_utils.get_secret("OPEN_API_KEY")
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    index = pinecone.Index(index_name)
    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")

    prompt = utils.augment_prompt(index, embed_model, query)
    chat = ChatOpenAI(
        openai_api_key=os.environ["OPENAI_API_KEY"], model="gpt-3.5-turbo"
    )

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
