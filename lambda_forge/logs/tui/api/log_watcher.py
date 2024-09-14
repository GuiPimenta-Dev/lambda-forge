import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from botocore.exceptions import ClientError


class ForgeError(Exception):
    """Custom error class for handling log-related exceptions."""

    def __init__(self, message: str):
        super().__init__(message)


class LogManager:
    def __init__(self, logfile: str):
        self.logfile = logfile

    def write_log_entry(self, log_entry: Dict):
        """
        Writes a single log entry to the logfile.

        :param log_entry: The log entry to write.
        """
        try:
            with open(self.logfile, "a") as file:
                json.dump(log_entry, file)
                file.write("\n")
            print(f"Log entry written to {self.logfile}")
        except IOError as e:
            raise ForgeError(f"Error writing log entry: {e}")

    def clear_logs(self):
        """
        Clears the contents of the logfile.
        """
        try:
            with open(self.logfile, "w") as file:
                file.write("")
        except IOError as e:
            raise ForgeError(f"Error clearing logs: {e}")


class CloudWatchLogFetcher:
    def __init__(self):
        self.client = boto3.client("logs")

    def load_project_name(self, config_file: str = "cdk.json") -> Optional[str]:
        """Load the project name from the configuration file."""
        try:
            with open(config_file, "r") as cdk_file:
                return json.load(cdk_file)["context"]["name"]
        except IOError as e:
            raise ForgeError(f"Error loading project name from {config_file}: {e}")

    def get_log_group_name(self, project: str, function_name: str) -> str:
        """Construct the log group name for a given Lambda function."""
        return f"/aws/lambda/{project}-{function_name}"

    def get_latest_log_stream(self, log_group_name: str) -> Optional[str]:
        """
        Get the latest log stream for the given log group.

        :param log_group_name: The log group name.
        :return: The latest log stream name, if available.
        """
        try:
            response = self.client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy="LastEventTime",
                descending=True,
                limit=1,
            )
            if "logStreams" in response and response["logStreams"]:
                return response["logStreams"][0]["logStreamName"]
        except ClientError as e:
            raise ForgeError(f"Error describing log streams for {log_group_name}: {e}")
        return None

    def fetch_log_events(
        self,
        log_group_name: str,
        log_stream_name: str,
        next_token: Optional[str] = None,
        start_time: Optional[int] = None,
    ) -> Optional[Dict]:
        """
        Fetch log events from a specific log stream.

        :param log_group_name: The log group name.
        :param log_stream_name: The log stream name.
        :param next_token: The token for the next batch of log events.
        :param start_time: The start time in milliseconds since the epoch.
        :return: The log events, if available.
        """
        data = {
            "logGroupName": log_group_name,
            "logStreamName": log_stream_name,
            "startFromHead": False,
        }

        if next_token:
            data["nextToken"] = next_token
        else:
            data["limit"] = 1

        try:
            return self.client.get_log_events(**data)
        except ClientError as e:
            raise ForgeError(
                f"Error fetching log events for {log_group_name}, {log_stream_name}: {e}"
            )

    def process_log_events(
        self,
        log_events: Dict,
        function_name: str,
        log_manager: LogManager,
        last_tokens: Dict[str, str],
    ) -> None:
        """Process log events and write them to a log file."""
        if not log_events or "events" not in log_events:
            return

        new_token = log_events["nextForwardToken"]
        if last_tokens[function_name] != new_token:
            last_tokens[function_name] = new_token

        for event in log_events["events"]:
            timestamp = datetime.utcfromtimestamp(
                event["timestamp"] / 1000.0
            ).isoformat()
            message = event["message"].strip()
            is_error = "ERROR" in message.upper()

            log_entry = {
                "function_name": function_name,
                "timestamp": timestamp,
                "message": message,
                "is_error": is_error,
            }

            log_manager.write_log_entry(log_entry)


class LogWatcher:
    def __init__(
        self,
        log_file_path: str,
        functions: List[Dict[str, str]],
        fetch_latest_only: bool = False,
    ):
        self.log_file_path = log_file_path
        self.functions = functions
        self.cloudwatch_client = CloudWatchLogFetcher()
        self.log_manager = LogManager(log_file_path)
        self.last_tokens: Dict[str, str] = {}
        if fetch_latest_only:
            self.log_manager.clear_logs()

    @property
    def project_name(self):
        return self.cloudwatch_client.load_project_name()

    def update_logs(self):
        """Main function to watch logs for a list of Lambda functions."""
        project = self.project_name

        if not project:
            raise ForgeError("Failed to load project name. Exiting.")

        for function in self.functions:
            function_name = function["name"]
            full_function_name = f"{project}-{function_name}"
            log_group_name = self.cloudwatch_client.get_log_group_name(
                project, function_name
            )
            log_stream_name = self.cloudwatch_client.get_latest_log_stream(
                log_group_name
            )

            if not log_stream_name:
                continue

            if full_function_name not in self.last_tokens:
                log_events = self.cloudwatch_client.fetch_log_events(
                    log_group_name, log_stream_name
                )
                if log_events:
                    self.last_tokens[full_function_name] = log_events[
                        "nextForwardToken"
                    ]
            else:
                log_events = self.cloudwatch_client.fetch_log_events(
                    log_group_name,
                    log_stream_name,
                    self.last_tokens[full_function_name],
                )

            if log_events:
                self.cloudwatch_client.process_log_events(
                    log_events, full_function_name, self.log_manager, self.last_tokens
                )
