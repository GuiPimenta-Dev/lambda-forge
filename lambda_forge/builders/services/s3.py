from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications

from lambda_forge.trackers import invoke, trigger


class S3:
    def __init__(self, scope, context) -> None:

        # self.s3 = s3.Bucket.from_bucket_arn(
        #     scope,
        #     "S3",
        #     bucket_arn=context.resources["arns"]["s3_arn"],
        # )
        ...

    @trigger(service="s3", trigger="bucket", function="function")
    def create_trigger(self, bucket, function, event=s3.EventType.OBJECT_CREATED):
        bucket = getattr(self, bucket)
        notifications = aws_s3_notifications.LambdaDestination(function)
        bucket.add_event_notification(event, notifications)
        bucket.grant_read(function)

    @invoke(service="s3", resource="bucket", function="function")
    def grant_write(self, bucket, function):
        bucket = getattr(self, bucket)
        bucket.grant_write(function)
