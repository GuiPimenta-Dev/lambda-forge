import aws_cdk as cdk
from infra.stacks.dev_stack import DevStack
from infra.stacks.staging_stack import StagingStack
from infra.stacks.prod_stack import ProdStack

app = cdk.App()

DevStack(app)
StagingStack(app)
ProdStack(app)

app.synth()