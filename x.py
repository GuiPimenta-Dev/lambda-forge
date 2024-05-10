import boto3
import uuid


def create_or_replace_bucket_with_trigger(lambda_arn):
    s3 = boto3.client("s3")
    lambda_client = boto3.client("lambda")
    account_id = "211125768252"

    # Create a unique bucket name
    new_bucket_name = f"live-s3-{uuid.uuid4()}"

    # Check for existing buckets and delete them if they match the naming pattern
    existing_buckets = s3.list_buckets()["Buckets"]
    for bucket in existing_buckets:
        if bucket["Name"].startswith("live-s3-"):
            # Check and empty the bucket before deletion
            object_list = s3.list_objects(Bucket=bucket["Name"])
            if "Contents" in object_list:
                for obj in object_list["Contents"]:
                    s3.delete_object(Bucket=bucket["Name"], Key=obj["Key"])
            print(f"Deleting bucket {bucket['Name']}")
            s3.delete_bucket(Bucket=bucket["Name"])

    # Create the new bucket
    s3.create_bucket(
        Bucket=new_bucket_name,
        CreateBucketConfiguration={"LocationConstraint": "us-east-2"},
    )
    print(f"Created new bucket {new_bucket_name}")

    # Set up the Lambda trigger
    events = [
        "s3:ObjectCreated:*",
        "s3:ObjectRemoved:*",
        "s3:ObjectRestore:*",
        "s3:ReducedRedundancyLostObject",
    ]

    lambda_config = {
        "LambdaFunctionArn": lambda_arn,
        "Events": events,
        "Filter": {
            "Key": {
                "FilterRules": [
                    {"Name": "prefix", "Value": ""},
                    {"Name": "suffix", "Value": ""},
                ]
            }
        },
    }

    # Add permission for S3 to invoke the Lambda function
    lambda_client.add_permission(
        FunctionName=lambda_arn,
        StatementId=f"{new_bucket_name}-invoke",
        Action="lambda:InvokeFunction",
        Principal="s3.amazonaws.com",
        SourceArn=f"arn:aws:s3:::{new_bucket_name}",
        SourceAccount=account_id
    )

    # Set the notification configuration on the bucket
    s3.put_bucket_notification_configuration(
        Bucket=new_bucket_name,
        NotificationConfiguration={"LambdaFunctionConfigurations": [lambda_config]},
    )
    print(f"Trigger created for bucket {new_bucket_name} and lambda {lambda_arn}")


# Example usage
lambda_arn = "arn:aws:lambda:us-east-2:211125768252:function:HelloAres-Live"
create_or_replace_bucket_with_trigger(lambda_arn)
