from infra.services import Services


class QrcodeConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Qrcode",
            path="./functions/images",
            description="Converts an image into a qr code",
            directory="qrcode",
            layers=[services.layers.qrcode_layer],
            environment={
                "BUCKET_NAME": services.s3.images_bucket.bucket_name,
            },
        )

        services.api_gateway.create_endpoint(
            "POST", "/images/qrcode", function, public=True
        )

        services.s3.grant_write("images_bucket", function)
