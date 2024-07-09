import aws_cdk as cdk

from infra.stacks.stack import Stack

app = cdk.App()

Stack(app)

app.synth()
