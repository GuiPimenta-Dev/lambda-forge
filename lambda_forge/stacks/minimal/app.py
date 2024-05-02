import aws_cdk as cdk
from infra.stacks.prod_stack import ProdStack

app = cdk.App()

ProdStack(app)

app.synth()
