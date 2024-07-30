import json
import os

import boto3

from . import utils
from decimal import Decimal


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")
    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME", "Dev-Transcriptions")
    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)

    body = json.loads(event["Records"][0]["body"])

    s3 = boto3.client("s3")
    s3_bucket = body["s3_bucket"]
    s3_key = body["s3_key"]
    s3_object = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    payload = json.loads(s3_object["Body"].read().decode("utf-8"))

    video_id = payload["video_id"]
    label = payload["label"]
    interval = payload["interval"]
    min_messages = payload["min_messages"]
    author_summary = payload["prompt"]
    chat = payload["messages"]

    messages = [message["message"] for message in chat]

    if len(messages) < int(min_messages):
        response = {
            "rating": "0",
            "reason": "Minimum number of messages not reached.",
            "chat_summary": "N/A",
        }

    else:
        response = utils.analyse_with_openai(author_summary, messages)

    comprehend = boto3.client('comprehend')
    messages_with_sentiments = []
    
    batch_size = 25
    
    # Process messages in batches
    for i in range(0, len(messages), batch_size):
        sentiment_batch = messages[i:i + batch_size]
        sentiments = comprehend.batch_detect_sentiment(TextList=sentiment_batch, LanguageCode="pt")["ResultList"]
        for message, sentiment in zip(sentiment_batch, sentiments):
            sentiment['SentimentScore'] = {k: Decimal(str(v)) for k, v in sentiment['SentimentScore'].items()}
            messages_with_sentiments.append({"message": message, "sentiment": sentiment})
    

    neutral = len([message for message in messages_with_sentiments if message["sentiment"]["Sentiment"] == "NEUTRAL"])
    positive = len([message for message in messages_with_sentiments if message["sentiment"]["Sentiment"] == "POSITIVE"])
    negative = len([message for message in messages_with_sentiments if message["sentiment"]["Sentiment"] == "NEGATIVE"])
    
    transcriptions_table.put_item(
        Item={
            "PK": f"{video_id}#INTERVAL={interval}",
            "SK": label,
            "messages": messages_with_sentiments,
            "rating": response["rating"],
            "neutral": neutral,
            "positive": positive,
            "negative": negative,
            "reason": response["reason"],
            "chat_summary": response["chat_summary"],
        }
    )
