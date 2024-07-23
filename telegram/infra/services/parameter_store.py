from aws_cdk import aws_ssm as ssm


class ParameterStore:
    def __init__(self, scope, context) -> None:

        self.chat_id = ssm.StringParameter.from_string_parameter_attributes(
            scope, "ChatIdParameter", parameter_name="chat-id"
        )
