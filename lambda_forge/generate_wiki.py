import sys
import json

if __name__ == "__main__":
    file_path = sys.argv[1]
    title = sys.argv[2]
    favicon = sys.argv[3]

    # Read the Markdown content from the file
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Escape single quotes in the content to prevent breaking the JS string
    # and convert newlines to \n so they are preserved in the JS string
    content_escaped = json.dumps(content)

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <link rel="icon" href="{favicon}" type="image/png"> 
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background-color: #f9f9f9;
            color: #333;
        }}
        #md-preview {{
            width: 100%;
            height: 90vh;
            background-color: #fff;
            border-radius: 8px;
            overflow: auto;
        }}
    </style>
</head>
<body>
    <div id="md-preview"></div>
    <script>
        const mdPreview = document.getElementById('md-preview');
        // Use the escaped Markdown content
        let initialMd = {content_escaped};

        // Function to render Markdown
        function renderMarkdown(md) {{
            mdPreview.innerHTML = marked.parse(md);
        }}

        // Initial render
        renderMarkdown(initialMd);
    </script>
</body>
</html>
"""

    # Save the HTML content to a file with UTF-8 encoding
    with open(f"{title}.html", "w", encoding='utf-8') as file:
        file.write(html_template)
