import boto3
import time
from datetime import datetime
import json

def watch_logs_for_functions(functions, log_file_path, stack, interval=1):
    cloudwatch_client = boto3.client('logs')
    last_tokens = {}

    with open(log_file_path, 'a') as log_file:
        while True:
            for function in functions:
                function_name = function['name']
                project = json.load(open("cdk.json", "r"))["context"]["name"]
                # full_function_name = f"{stack}-{project}-{function_name}"
                full_function_name = f"{project}-{function_name}"
                log_group_name = f"/aws/lambda/{full_function_name}"

                try:
                    # Get the log streams for the Lambda function
                    log_streams = cloudwatch_client.describe_log_streams(
                        logGroupName=log_group_name,
                        orderBy='LastEventTime',
                        descending=True,
                        limit=1  # Get the latest log stream
                    )
                    
                    if 'logStreams' in log_streams and log_streams['logStreams']:
                        log_stream_name = log_streams['logStreams'][0]['logStreamName']
                        
                        # Set the start token to None for the first run, capturing the latest log stream but not processing it
                        if full_function_name not in last_tokens:
                            log_events = cloudwatch_client.get_log_events(
                                logGroupName=log_group_name,
                                logStreamName=log_stream_name,
                                limit=1,  # Fetch only the latest event to get the token
                                startFromHead=False
                            )
                            # Initialize the token with the nextForwardToken, effectively skipping initial logs
                            last_tokens[full_function_name] = log_events['nextForwardToken']
                        else:
                            # Get the log events from the latest log stream
                            log_events = cloudwatch_client.get_log_events(
                                logGroupName=log_group_name,
                                logStreamName=log_stream_name,
                                nextToken=last_tokens[full_function_name],
                                startFromHead=False
                            )
                            
                            # Update the last token for the function
                            last_tokens[full_function_name] = log_events['nextForwardToken']
                            
                            for event in log_events['events']:
                                timestamp = datetime.utcfromtimestamp(event['timestamp'] / 1000.0).isoformat()
                                message = event['message'].strip()
                                is_error = "ERROR" in message.upper()
                                
                                log_entry = {
                                    "function_name": full_function_name,
                                    "timestamp": timestamp,
                                    "message": message,
                                    "is_error": is_error
                                }
                                
                                json.dump(log_entry, log_file)
                                log_file.write('\n')
                                print(log_entry)
                
                except Exception as e:
                    error_entry = {
                        "function_name": full_function_name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": str(e),
                        "is_error": True
                    }
                    json.dump(error_entry, log_file)
                    log_file.write('\n')
                    print(f"Error retrieving logs for {full_function_name}: {str(e)}")

            time.sleep(interval)
