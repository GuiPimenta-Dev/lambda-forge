from aws_cdk import aws_kms as kms


class KMS:
    def __init__(self, scope, context) -> None:

        # self.kms = kms.Key.from_key_arn(
        #     scope,
        #     "KMS",
        #     key_arn=context.resources["arns"]["kms_arn"],
        # )
        ...
