import json
from dataclasses import dataclass
import sm_utils
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from . import utils

@dataclass
class Input:
    pass

@dataclass
class Output:
    message: str


def lambda_handler(event, context):
    
    PINECONE_API_KEY = sm_utils.get_secret("PINECONE_API_KEY")
    OPEN_API_KEY = sm_utils.get_secret("OPEN_API_KEY")
    PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "lambda-forge-telegram")
    VISITED_URLS_TABLE_NAME = os.environ.get("VISITED_URLS_TABLE_NAME", "VisitedURLs")
    
    pc = Pinecone(api_key=PINECONE_API_KEY)

    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536, 
            metric="cosine", 
            spec=ServerlessSpec(
                cloud="aws", 
                region="us-east-1"
            ) 
        ) 

    
    
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello World!"}),
        "headers": {"Access-Control-Allow-Origin": "*"}
    }

event = {
    "body": {
        "job_id": "a935b50c-f705-4347-8c8b-bee850311c98",
        "name": "lambda-forge"
    }
}
lambda_handler(event, None)