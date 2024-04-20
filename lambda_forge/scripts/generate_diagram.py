import subprocess
import sys


# Get CDK stacks using AWS CLI
def get_stacks():
    result = subprocess.run(["cdk", "list"], capture_output=True, text=True)
    return result.stdout.splitlines()


# Read environment from command-line arguments
if len(sys.argv) != 2:
    print("Usage: python script.py <environment>")
    sys.exit(1)

environment = sys.argv[1]

# Get all stacks
all_stacks = get_stacks()

stacks_to_exclude = [stack for stack in all_stacks if environment.lower() not in stack.lower()]

run = ["npx", "cdk-dia", "--exclude"]
for stack in stacks_to_exclude:
    run.append(stack)

subprocess.run(run)
