import json
import os
from dataclasses import dataclass

import boto3
from langchain_openai import OpenAIEmbeddings
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

    OPENAI_API_KEY = get_secret("OPEN_API_KEY")
    PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "lambda-forge-telegram")
    VISITED_URLS_TABLE_NAME = os.environ.get("VISITED_URLS_TABLE_NAME", "ScrapedURLs")
    PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    pinecone = Pinecone(api_key=PINECONE_API_KEY)

    index = utils.create_pinecone_index(pinecone, PINECONE_INDEX_NAME)
    data = utils.query_all_data_from_dynamo(VISITED_URLS_TABLE_NAME, "0da893aa-7fc0-4c0a-9d5a-dd2528f98a73")

    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")

    utils.store_knowledge_in_pinecone(index, data, embed_model)

    return {"statusCode": 200, "headers": {"Access-Control-Allow-Origin": "*"}}
