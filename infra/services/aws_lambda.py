import shutil

from aws_cdk import Duration, RemovalPolicy
from aws_cdk.aws_cloudwatch import Alarm, ComparisonOperator
from aws_cdk.aws_cloudwatch_actions import SnsAction
from aws_cdk.aws_lambda import Code, Function, Runtime


class AWSLambda:
    def __init__(self, scope, stage, alarm, versioning, sns) -> None:
        self.scope = scope
        self.stage = stage
        self.alarm = alarm
        self.versioning = versioning
        self.sns = sns
        self.functions = []

    def create_function(
        self,
        name,
        path,
        description,
        directory=None,
        timeout=Duration.minutes(1),
        layers=[],
        environment={},
    ):
        full_path = (
            f"{path}/{directory}/main.lambda_handler"
            if directory
            else f"{path}/main.lambda_handler"
        )
        repo_name = self.scope.node.try_get_context("name")
        handler = (
            f"src.{directory}.main.lambda_handler"
            if directory
            else "src.main.lambda_handler"
        )
        function = Function(
            scope=self.scope,
            id=name,
            description=description,
            function_name=f"{self.stage}-{repo_name}-{name}",
            runtime=Runtime.PYTHON_3_9,
            handler=handler,
            environment=environment,
            code=Code.from_asset(path=self.__top_level_path(path)),
            layers=layers,
            timeout=timeout,
        )

        self.functions.append(
            {
                "file_path": full_path,
                "name": name,
                "description": description,
            }
        )

        if self.alarm:
            self.__create_alarm(function, name)

        if self.versioning:
            self.__create_versioning(function)

        return function

    def __create_alarm(self, function, function_name):
        alarm = Alarm(
            scope=self.scope,
            id=f"{self.stage}-{function_name}-Alarm",
            metric=function.metric_errors(),
            threshold=1,
            evaluation_periods=1,
            alarm_description="The latest deployment errors > 0",
            alarm_name=f"{self.stage}-{function_name}-Alarm",
            comparison_operator=ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )

        alarm.add_alarm_action(SnsAction(topic=self.sns.alarm_topic))

    @staticmethod
    def __create_versioning(function):
        new_version = function.current_version
        new_version.apply_removal_policy(RemovalPolicy.RETAIN)

    @staticmethod
    def __top_level_path(src):
        path = f"./.fc/{src.split('functions/')[1]}"
        shutil.copytree(src, f"{path}/src", dirs_exist_ok=True)
        return path
