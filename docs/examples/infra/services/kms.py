from aws_cdk import aws_kms as kms


class KMS:
    def __init__(self, scope, context) -> None:

        self.auth_key = kms.Key.from_key_arn(
            scope,
            "SignUpKey",
            key_arn="arn:aws:kms:us-east-2:211125768252:key/bb085039-a653-4b38-abad-b6dd4ce11ea4",
        )
