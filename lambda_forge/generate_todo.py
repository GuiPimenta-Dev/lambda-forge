import json
import os
import re


# Define the function to check for keywords and capture subsequent comments until a blank line
def check_for_keywords_with_comments(file_path):
    keywords_with_comments = {}
    with open(file_path, "r") as file:
        lines = file.readlines()
        keyword = None
        comment_lines = []
        for line in lines:
            # Check if we're currently capturing comments for a keyword
            if keyword is not None:
                if line.strip() == "":
                    # If we encounter a blank line, save the comments we've collected so far
                    if comment_lines:
                        if keyword not in keywords_with_comments:
                            keywords_with_comments[keyword] = []
                        keywords_with_comments[keyword].append(" ".join(comment_lines))
                        comment_lines = []
                    keyword = None  # Reset the keyword after capturing comments
                else:
                    # Remove leading '#' and whitespace from the comment
                    cleaned_line = line.strip().lstrip("#").strip()
                    comment_lines.append(cleaned_line)
            else:
                # Look for a keyword in the current line
                for kw in ["help", "improve", "waiting", "todo", "fixme"]:
                    if f"# {kw.upper()}" in line or f"# {kw}" in line:
                        keyword = kw
                        # If the keyword is found, check if there's a comment on the same line following it
                        comment_part = line.split(f"# {kw.upper()}")[-1].strip()
                        if not comment_part:  # If no comment on the same line, continue to the next line
                            comment_part = line.split(f"# {kw}")[-1].strip()
                        if comment_part:  # If there's a comment part on the same line, add it
                            comment_lines.append(comment_part)
                        break  # Break after finding the first keyword to not overwrite it if there are multiple

    return keywords_with_comments


def generate_html(keywords_with_comments):
    html = """
    <html>
    <head>
        <title>To Do</title>
        <link href="https://fonts.googleapis.com/css?family=Roboto&display=swap" rel="stylesheet">
        <link rel="icon" type="image/png" href="data:image/png;base64,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">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                margin: 20px;
            }
            .comment {
                border: 1px solid #ddd;
                margin: 10px 0px;
                padding: 10px;
                border-radius: 5px;
                color: #333; /* Default font color */
            }
            .file-path {
                margin-top: 20px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
    """
    for file_path, keywords in keywords_with_comments.items():
        clean_file_path = file_path.lstrip("./")  # Adjust file path presentation
        html += f'<div class="file-path">{clean_file_path}</div>'
        for keyword, comments in keywords.items():
            bg_color, font_color = (
                "#FFFFFF",
                "#000000",
            )  # Default colors

            if keyword == "help":
                bg_color, font_color = "#FFD700", "#000000"
            elif keyword == "improve":
                bg_color, font_color = "#90EE90", "#000000"
            elif keyword == "waiting":
                bg_color, font_color = "#87CEEB", "#000000"
            elif keyword == "todo":
                bg_color, font_color = "#FFA07A", "#000000"
            elif keyword == "fixme":
                bg_color, font_color = "#FF6347", "#000000"

            for comment in comments:
                # Ensure only one colon is present after the keyword
                formatted_comment = f"<strong>{keyword.upper()}</strong>: {comment.replace(':','')}"
                html += f'<div class="comment" style="background-color: {bg_color}; color: {font_color};">{formatted_comment}</div>'
    html += "</body></html>"
    return html


# Define the function to iterate through files and generate HTML with keywords and comments
def iterate_files_and_generate_html(files):
    all_keywords_with_comments = {}
    for file_data in files:
        file_path = os.path.join(file_data["path"], f"main.py")
        if os.path.exists(file_path):
            keywords_with_comments = check_for_keywords_with_comments(file_path)
            if keywords_with_comments:
                all_keywords_with_comments[file_path] = keywords_with_comments
    html = generate_html(all_keywords_with_comments)
    with open("todo.html", "w") as html_file:
        html_file.write(html)


# Call the function to iterate through files and generate HTML with keywords and comments
with open("cdk.json", "r") as json_file:
    context = json.load(json_file)["context"]
    functions = context["functions"]

iterate_files_and_generate_html(functions)
