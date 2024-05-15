import json
import os
import time

from lambda_forge.printer import Printer

printer = Printer()


def create_cli_header(title):
    # Get the current size of the terminal
    terminal_width = os.get_terminal_size().columns

    # Prepare the header components
    title = f" {title} "  # Add a space before and after the title
    title_length = len(title)

    if title_length >= terminal_width:
        # If the title is too long, truncate it
        title = title[: terminal_width - 4] + "... "

    # Calculate how much padding is needed
    padding = (terminal_width - len(title)) // 2

    # Create the top and bottom borders
    border = "#" * terminal_width

    # Create the title line, centering the title
    title_line = "#" * padding + title + "#" * (terminal_width - len(title) - padding)

    # Construct the full header
    header = f"{border}\n{title_line}\n{border}"
    return header


def print_service(event):
    records = json.loads(event)
    event = json.dumps(json.loads(event), indent=2)
    if "Records" in event:
        record = records["Records"][0]
        if "s3" in record:
            header = create_cli_header("S3")
            printer.print(header, "orange")
            printer.print(event, "orange", 1)
        elif record.get("eventSource") == "aws:dynamodb":
            header = create_cli_header("DYNAMO")
            printer.print(header, "blue")
            printer.print(event, "blue", 1)
        elif record.get("eventSource") == "aws:sqs":
            header = create_cli_header("SQS")
            printer.print(header, "cyan")
            printer.print(event, "cyan", 1)
        elif record.get("EventSource") == "aws:sns":
            header = create_cli_header("SNS")
            printer.print(header, "magenta")
            printer.print(event, "magenta", 1)

    elif "event.bridge" in event:
        header = create_cli_header("Event Bridge")
        printer.print(header, "lime")
        printer.print(event, "lime", 1)

    elif "httpMethod" in event:
        header = create_cli_header("API GATEWAY")
        printer.print(header, "yellow")
        printer.print(event, "yellow", 1)

    else:
        header = create_cli_header("LAMBDA")
        color = "green"
        if '"statusCode": 500' in event:
            color = "red"

        printer.print(header, color)
        printer.print(event, color, 1)

    printer.br(2)


def tail_f(filename):
    printer.show_banner("Live Logs")
    """Implements tail -f with color-coded output based on the service."""
    with open(filename, "r") as file:
        # Move the cursor to the end of the file
        file.seek(0, 2)

        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                continue

            print_service(line)
