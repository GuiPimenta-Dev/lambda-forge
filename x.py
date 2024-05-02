import re
import click


account = click.prompt("AWS Account ID", type=lambda value: value if re.match(r'^\d{12}$', value) else click.BadParameter('Account ID must be a 12-digit number.'))
