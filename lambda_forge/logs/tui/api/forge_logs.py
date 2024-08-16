from collections import defaultdict
from enum import Enum
from typing import Dict, Iterable, List, Optional, Self
from ._test_data import log_groups, cloudwatch_logs


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
        self.timestamp = timestamp / 1000 # Convert to seconds

    @classmethod
    def parse(cls, timestamp: int, message: str) -> Self:
        log_type, message = message.split(" ", 1)
        log_type = LogType(log_type)

        return cls(log_type, message, int(timestamp))


class ForgeLogsAPI:
    def __init__(self, params: Optional[Dict]) -> None:
        self.params = params
        self.d = defaultdict(int)

    def get_lambdas(self) -> List[LambdaGroup]:
        return [LambdaGroup(group, name) for group, name in log_groups]

    # NOTE: Implement this function (@gui)
    def _get_logs(self, lambda_group: str) -> List[Dict]:
        self.d[lambda_group] += 1

        def _get_index(name):
            return [i for i, _ in log_groups].index(name)

        if _get_index(lambda_group) % 2 == 0:
            return list(reversed(cloudwatch_logs))[0 : self.d[lambda_group]]
        else:
            return cloudwatch_logs[0 : self.d[lambda_group]]

    def get_logs(self, lambda_group: str) -> Iterable[CloudWatchLog]:
        logs = self._get_logs(lambda_group)

        for log in logs:
            yield CloudWatchLog.parse(
                log["timestamp"],
                log["message"],
            )
