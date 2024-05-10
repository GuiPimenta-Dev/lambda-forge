import subprocess

if __name__ == "__main__":
    subprocess.run(["python", "generate_api_docs.py"], check=True)
    subprocess.run(["redoc-cli", "bundle", "-o", "redoc.html", "docs.yaml"], check=True)
