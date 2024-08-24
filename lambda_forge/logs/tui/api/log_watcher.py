import boto3
from datetime import datetime
import json
from typing import Dict, List, Optional
from botocore.exceptions import ClientError


def load_project_name(config_file: str = "cdk.json") -> Optional[str]:
    """Load the project name from the configuration file."""
    with open(config_file, "r") as cdk_file:
        return json.load(cdk_file)["context"]["name"]


def get_log_group_name(project: str, function_name: str) -> str:
    """Construct the log group name for a given Lambda function."""
    return f"/aws/lambda/{project}-{function_name}"


def get_latest_log_stream(cloudwatch_client, log_group_name: str) -> Optional[str]:
    """Get the latest log stream for the given log group."""
    try:
        response = cloudwatch_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy="LastEventTime",
            descending=True,
            limit=1,
        )
        if "logStreams" in response and response["logStreams"]:
            return response["logStreams"][0]["logStreamName"]
    except ClientError as e:
        raise ValueError(f"Error describing log streams for {log_group_name}: {e}")
    return None


def fetch_log_events(
    cloudwatch_client,
    log_group_name: str,
    log_stream_name: str,
    next_token: Optional[str] = None,
) -> Optional[Dict]:
    """Fetch log events from a specific log stream."""

    data = dict(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        startFromHead=False,
    )

    try:
        if next_token:
            extra_data = dict(nextToken=next_token)
        else:
            extra_data = dict(limit=1)

        return cloudwatch_client.get_log_events(**(data | extra_data))
    except ClientError as e:
        raise ValueError(
            f"Error fetching log events for {log_group_name}, {log_stream_name}: {e}"
        )


def process_log_events(
    log_events: Dict, function_name: str, log_file, last_tokens: Dict[str, str]
) -> None:
    """Process log events and write them to a log file."""
    if not log_events or "events" not in log_events:
        return

    new_token = log_events["nextForwardToken"]
    if last_tokens[function_name] != new_token:
        last_tokens[function_name] = new_token

    for event in log_events["events"]:
        timestamp = datetime.utcfromtimestamp(event["timestamp"] / 1000.0).isoformat()
        message = event["message"].strip()
        is_error = "ERROR" in message.upper()

        log_entry = {
            "function_name": function_name,
            "timestamp": timestamp,
            "message": message,
            "is_error": is_error,
        }

        json.dump(log_entry, log_file)
        log_file.write("\n")
        log_file.flush()


def watch_logs_for_functions(
    functions: List[Dict[str, str]], log_file_path: str, stack: str
) -> None:
    """Main function to watch logs for a list of Lambda functions."""
    cloudwatch_client = boto3.client("logs")
    last_tokens: Dict[str, str] = {}
    project = load_project_name()

    if not project:
        raise ValueError("Failed to load project name. Exiting.")

    with open(log_file_path, "a") as log_file:
        for function in functions:
            function_name = function["name"]
            full_function_name = f"{project}-{function_name}"
            log_group_name = get_log_group_name(project, function_name)
            log_stream_name = get_latest_log_stream(cloudwatch_client, log_group_name)

            if not log_stream_name:
                continue

            if full_function_name not in last_tokens:
                log_events = fetch_log_events(
                    cloudwatch_client,
                    log_group_name,
                    log_stream_name,
                )
                if log_events:
                    last_tokens[full_function_name] = log_events["nextForwardToken"]
            else:
                log_events = fetch_log_events(
                    cloudwatch_client,
                    log_group_name,
                    log_stream_name,
                    last_tokens[full_function_name],
                )

            assert log_events is not None
            process_log_events(log_events, full_function_name, log_file, last_tokens)
