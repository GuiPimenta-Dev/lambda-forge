import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
import sm_utils


def lambda_handler(event, context):
    # Initialize the S3 client
    s3_client = boto3.client("s3")

    # Fetch the SMTP details from the environment variables
    SMTP_HOST = os.environ["SMTP_HOST"]
    SMTP_PORT = os.environ["SMTP_PORT"]

    # Get the secret name from env variable
    SECRET_NAME = os.environ["SECRET_NAME"]

    # Get the secret from sm_utils layer
    secret = sm_utils.get_secret(SECRET_NAME)

    SMTP_USER = secret["email"]
    SMTP_PASS = secret["password"]

    # Extract the bucket name and the object key from the event
    record = event["Records"][0]
    bucket_name = record["s3"]["bucket"]["name"]
    object_key = record["s3"]["object"]["key"]

    # Fetch the image from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

    # Extract the receiver email from the metadata
    receiver = response["Metadata"]["email"]

    # Create the multipart email
    msg = MIMEMultipart()
    sender_name = "Lambda Forge"

    # Set the 'From' field, including both the name and the email:
    msg["From"] = f"{sender_name} <{SMTP_USER}>"
    msg["To"] = receiver
    msg["Subject"] = "Image Processed Successfully!"

    # Join the current directory with the filename to get the full path of the HTML file
    current_directory = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_directory, "template.html")

    # Read the HTML content
    html = open(html_path).read()
    msg.attach(MIMEText(html, "html"))

    # Attach the image
    image_data = response["Body"].read()
    file_name = object_key.split("/")[-1]
    part = MIMEApplication(image_data, Name=file_name)
    part["Content-Disposition"] = f'attachment; filename="{file_name}"'
    msg.attach(part)

    # Send the email via Gmail's SMTP server, or use another server if not using Gmail
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, receiver, msg.as_string())