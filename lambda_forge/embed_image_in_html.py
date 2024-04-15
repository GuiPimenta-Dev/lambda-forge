import base64
import sys


def embed_image_in_html(image_path, html_path):
    # Read the content of the image file
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        # Encode the image data as base64
        encoded_image = base64.b64encode(image_data).decode()

        # HTML template with embedded image
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Diagram</title>
    <style>
        /* Reset default margin and padding */
        body, html {{
            margin: 0;
            padding: 0;
        }}
        /* Center the image horizontally */
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #FFFFFF; /* Set background color */
        }}
        /* Adjust the size of the image */
        img {{
            max-width: 100%;
            max-height: 100%;
            transition: transform 0.3s ease; /* Smooth transition for zoom effect */
        }}
        /* Zoom buttons */
        .zoom-buttons {{
            position: fixed;
            top: 20px;
            left: 20px;
        }}
    </style>
</head>
<body>
    <!-- Image container with zoom and drag functionality -->
    <div id="image-container">
        <img src="data:image/png;base64,{encoded_image}" alt="Embedded Image">
    </div>
    
    <script>
        var scale = 1;
        var imageContainer = document.getElementById("image-container");
        var isDragging = false;
        var startPos = {{ x: 0, y: 0 }};
        var translate = {{ x: 0, y: 0 }};
        var prevTranslate = {{ x: 0, y: 0 }};

        function setTransform() {{
            imageContainer.style.transform = `scale(${{scale}}) translate(${{translate.x}}px, ${{translate.y}}px)`;
        }}

        imageContainer.addEventListener("mousedown", function(event) {{
            isDragging = true;
            startPos.x = event.clientX - prevTranslate.x;
            startPos.y = event.clientY - prevTranslate.y;
            event.preventDefault(); // Prevent text selection
        }});

        window.addEventListener("mousemove", function(event) {{
            if (isDragging) {{
                translate.x = event.clientX - startPos.x;
                translate.y = event.clientY - startPos.y;
                setTransform();
            }}
        }});

        window.addEventListener("mouseup", function() {{
            isDragging = false;
            prevTranslate.x = translate.x;
            prevTranslate.y = translate.y;
        }});

        function zoomIn(event) {{
            scale += 0.09;
            setTransform();
        }}

        function zoomOut(event) {{
            if (scale > 0.2) {{
                scale -= 0.09;
                setTransform();
            }}
        }}

        // Add event listener for mouse wheel zoom
        imageContainer.addEventListener("wheel", function(event) {{
            var e = window.event || event;
            var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));
            
            if (delta > 0) {{
                zoomIn(event);
            }} else {{
                zoomOut(event);
            }}

            event.preventDefault();
        }});
    </script>
</body>
</html>
"""

    # Write the HTML content to a file
    with open(html_path, "w") as html_file:
        html_file.write(html_template)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <image_path> <html_path>")
        sys.exit(1)

    # Path to the image file
    image_path = sys.argv[1]
    # Path to the HTML file to be created
    html_path = sys.argv[2]

    # Call the function to embed the image in HTML
    embed_image_in_html(image_path, html_path)
