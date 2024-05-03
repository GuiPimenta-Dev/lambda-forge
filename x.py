# import json
# import click
# from lambda_forge.logs import Logger
# import boto3
# import ast


# sns = boto3.client("sns", region_name="us-east-2")
# logger = Logger()
# topic_arn = "arn:aws:sns:us-east-2:211125768252:Live-Server-Topic"
# message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
# subject = click.prompt(click.style("Subject", fg=(37, 171, 190)), type=str, default="", show_default=False)
# message_attributes = click.prompt(click.style("Message Attributes", fg=(37, 171, 190)), type=str, default="", show_default=False)
# if message_attributes and not isinstance(message_attributes, dict):

    
#   sns.publish(
#       TopicArn=topic_arn, Message=message, Subject=subject, MessageAttributes=message_attributes
#   )
  
# else:
#   sns.publish(TopicArn=topic_arn, Message=message, Subject=subject)

# payload = {"message": message, "subject": subject, "message_attributes": message_attributes}
# logger.log(json.dumps(payload, indent=4), "black", 1, 1)

import json

def convert_to_dict(input_string):
    try:
        # Try to convert the input string to a dictionary
        result_dict = json.loads(input_string)
    except json.JSONDecodeError:
        # Raise an error if the input is not a valid JSON
        raise ValueError("Input string could not be converted to a dictionary")
    return result_dict

# Example usage
# input_string = '{"key": "value"}'  # This should work
input_string = "3"  # This should raise an error

try:
    result = convert_to_dict(input_string)
    print("Converted Dictionary:", result)
except ValueError as e:
    print(e)
