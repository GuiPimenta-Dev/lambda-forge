from enum import Enum
from typing import Dict, Iterable, List, Optional, Self


class LogType(Enum):
    ERROR = "[ERROR]"
    START = "START"
    END = "END"
    REPORT = "REPORT"
    INIT_START = "INIT_START"


class LambdaGroup:
    def __init__(self, name: str, group: str) -> None:
        self.name = name
        self.group = group


class CloudWatchLog:

    def __init__(self, log_type: LogType, message: str, timestamp: int) -> None:
        self.log_type = log_type
        self.message = message
        self.timestamp = timestamp

    @classmethod
    def parse(cls, timestamp: int, message: str) -> Self:
        log_type, message = message.split(" ", 1)
        log_type = LogType(log_type)

        return cls(log_type, message, timestamp)


class ForgeLogsAPI:
    def __init__(self, params: Optional[Dict]) -> None:
        self.params = params

    def get_lambdas(self) -> List[LambdaGroup]:
        return []

    def _get_logs(self, lambda_group: str) -> List[Dict]:
        return []

    def get_logs(self, lambda_group: str) -> Iterable[CloudWatchLog]:
        logs = self._get_logs(lambda_group)

        for log in logs:
            yield CloudWatchLog.parse(
                log["timestamp"],
                log["message"],
            )
