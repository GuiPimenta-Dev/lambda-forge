import json
import os

import sm_utils
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

from . import utils


def lambda_handler(event, context):
    
    OPENAI_API_KEY = sm_utils.get_secret("OPEN_API_KEY")
    VISITED_URLS_TABLE_NAME = os.environ.get("VISITED_URLS_TABLE_NAME", "ScrapedURLs")
    PINECONE_API_KEY = sm_utils.get_secret("PINECONE_API_KEY")
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    body = json.loads(event["body"])
    job_id = body.get("job_id")
    pinecone_index_name = body.get("index_name", "lambda-forge-telegram")
    
    pinecone = Pinecone(api_key=PINECONE_API_KEY)

    index = utils.create_pinecone_index(pinecone, pinecone_index_name)
    data = utils.query_all_data_from_dynamo(VISITED_URLS_TABLE_NAME, job_id)

    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")

    utils.store_knowledge_in_pinecone(index, data, embed_model)

    return {"statusCode": 200, "headers": {"Access-Control-Allow-Origin": "*"}}
