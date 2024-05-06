import click

# This retrieves a text stream from standard input (stdin)
stdin_text = click.get_text_stream("stdin")

# This retrieves a binary stream from standard output (stdout)
stdout_binary = click.get_binary_stream("stdout")
