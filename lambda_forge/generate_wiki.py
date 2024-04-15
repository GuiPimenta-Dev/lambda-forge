import sys


if __name__ == "__main__":

    file = sys.argv[1]
    title = sys.argv[2]
    favicon = sys.argv[3]
    
    with open(file, "r") as file:
        content = file.read()

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
            border: 1px solid #ddd;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: auto;
        }}
    </style>
</head>
<body>
    <div id="md-preview"></div>
    <script>
        const mdPreview = document.getElementById('md-preview');
        let initialMd = `{content}`;

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

    # Save the HTML content to a file
    with open(f"{title}.html", "w") as file:
        file.write(html_template)
