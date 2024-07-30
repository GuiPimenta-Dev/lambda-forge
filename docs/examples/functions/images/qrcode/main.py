import hashlib
import json
import os
from dataclasses import dataclass
from io import BytesIO

import boto3
import qrcode


@dataclass
class Input:
    url: str
    email: str


@dataclass
class Output:
    pass


def lambda_handler(event, context):

    # Parse the input event to get the URL of the image and the S3 bucket name
    body = json.loads(event["body"])
    url = body.get("url")

    # Retrieve the S3 bucket name from environment variables
    bucket_name = os.environ.get(
        "BUCKET_NAME", "live-lambda-forge-examples-images-bucket"
    )

    # Generate QR code from the image
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()

    # Create an image from the QR code
    qr_image = qr.make_image()

    # Convert the QR code image to bytes
    qr_byte_arr = BytesIO()
    qr_image.save(qr_byte_arr)
    qr_byte_arr = qr_byte_arr.getvalue()

    # Create the file name with a hash based on the input URL
    file_name = f"{hashlib.md5(url.encode()).hexdigest()}.jpg"

    # Initialize the S3 client
    s3_client = boto3.client("s3")

    # Upload the QR code image to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=qr_byte_arr,
        ContentType="image/png",
        Metadata={"url": url, "email": body.get("email")},
    )

    return {"statusCode": 200}
