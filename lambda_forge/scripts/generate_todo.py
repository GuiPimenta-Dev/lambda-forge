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


if __name__ == "__main__":
    with open("cdk.json", "r") as json_file:
        context = json.load(json_file)["context"]
        functions = context["functions"]

    iterate_files_and_generate_html(functions)
