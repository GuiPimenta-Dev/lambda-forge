from datetime import datetime
from collections import defaultdict
from json import loads as json_loads
from enum import Enum
from typing import Dict, Iterable, List
from .log_watcher import LogWatcher
from .lambda_fetcher import list_lambda_functions


class LogType(Enum):
    ERROR = "[ERROR]"
    START = "START"
    END = "END"
    REPORT = "REPORT"
    INIT_START = "INIT_START"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def get(cls, value):
        """
        Safely get an enum member by value. Return UNKNOWN if value is not found.
        """
        try:
            return LogType(value)
        except ValueError:
            return LogType.UNKNOWN


class CloudWatchLog:

    def __init__(self, function_name, log_type, message, timestamp, is_error) -> None:
        self.function_name = function_name
        self.log_type = log_type
        self.message = message
        self.timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        self.is_error = is_error

    @classmethod
    def parse(cls, log: Dict):
        function_name = log["function_name"]
        timestamp = log["timestamp"]
        message = log["message"]
        is_error = log["is_error"]
        if is_error:
            log_type = LogType.ERROR
        else:
            log_type = LogType(message.split(" ")[0])

        return cls(function_name, log_type, message, timestamp, is_error)


class ForgeLogsAPI:
    def __init__(self, functions, log_path: str, stack: str, show_all: bool) -> None:
        self.log_path = log_path
        self.stack = stack
        self.log_watcher = LogWatcher(log_path, functions, fetch_latest_only=not show_all)
        self.d = defaultdict(int)

    def clear_logs(self):
        self.log_watcher.log_manager.clear_logs()

    def update_logs(self):
        self.log_watcher.update_logs()

    def get_lambdas(self) -> List[str]:
        return list_lambda_functions(self.stack)

    def _get_logs(self) -> List[CloudWatchLog]:
        logs = []

        with open(self.log_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                data = json_loads(line)
                log_obj = CloudWatchLog.parse(data)
                logs.append(log_obj)

        return logs

    def get_logs(self, lambda_group: str) -> Iterable[CloudWatchLog]:
        logs = [i for i in self._get_logs() if i.function_name == lambda_group]
        return logs
