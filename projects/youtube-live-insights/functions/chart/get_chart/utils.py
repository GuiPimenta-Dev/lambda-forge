import boto3


def query_all_items(table, partition_key, interval):
    items = []
    last_evaluated_key = None
    while True:
        if last_evaluated_key:
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(f"{partition_key}#INTERVAL={interval}"),
                ProjectionExpression="SK, rating, messages, chat_summary, reason",
                ExclusiveStartKey=last_evaluated_key,
            )
        else:
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(f"{partition_key}#INTERVAL={interval}"),
                ProjectionExpression="SK, rating, messages, chat_summary, reason",
            )

        items.extend(response["Items"])

        if "LastEvaluatedKey" not in response:
            break

        last_evaluated_key = response["LastEvaluatedKey"]

    filtered_data = [item for item in items if item["rating"] != "0"]

    return filtered_data
