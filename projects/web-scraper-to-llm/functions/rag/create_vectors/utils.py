import boto3
import pandas as pd
from pinecone import ServerlessSpec
from tqdm.auto import tqdm  # for progress bar


def create_pinecone_index(pinecone, index_name):
    if index_name not in pinecone.list_indexes().names():
        print(f"Creating Pinecone index {index_name}")
        pinecone.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    index = pinecone.Index(index_name)
    return index


def query_all_data_from_dynamo(table_name, partition_key_value):
    dynamodb = boto3.client("dynamodb")

    all_items = []
    last_evaluated_key = None

    while True:
        if last_evaluated_key:
            response = dynamodb.query(
                TableName=table_name,
                KeyConditionExpression="PK = :pk",
                ExpressionAttributeValues={":pk": {"S": partition_key_value}},
                ExclusiveStartKey=last_evaluated_key,
            )
        else:
            response = dynamodb.query(
                TableName=table_name,
                KeyConditionExpression="PK = :pk",
                ExpressionAttributeValues={":pk": {"S": partition_key_value}},
            )

        items = response.get("Items", [])
        all_items.extend(items)

        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break

    print(f"Found {len(all_items)} items in DynamoDB")
    return all_items


def store_knowledge_in_pinecone(index, data, embed_model):
    data = pd.DataFrame(data)
    batch_size = 5
    for i in tqdm(range(0, len(data), batch_size)):
        i_end = min(len(data), i + batch_size)
        batch = data.iloc[i:i_end]
        ids = []
        texts = []
        metadata = []
        for i, x in batch.iterrows():
            try:
                texts.append(x["content"]["S"])
                ids.append(x["SK"]["S"])
                metadata.append(
                    {
                        "text": x["content"]["S"],
                        "url": x["SK"]["S"],
                    }
                )
            except Exception as e:
                print(f"Error processing item {x}: {e}")
                continue
        embeds = embed_model.embed_documents(texts)
        try:
            index.upsert(vectors=zip(ids, embeds, metadata))
        except Exception as e:
            print(f"Error upserting batch: {e}")
            continue
