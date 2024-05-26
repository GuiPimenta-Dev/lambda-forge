from aws_cdk import aws_s3 as s3

from lambda_forge.services import Bucket


class S3(Bucket):
    def __init__(self, scope, context) -> None:
        super().__init__(scope, context)

        # self.s3 = s3.Bucket.from_bucket_arn(
        #     scope,
        #     "S3",
        #     bucket_arn=context.resources["arns"]["s3_arn"],
        # )
        ...
