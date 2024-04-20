import subprocess

if __name__ == "__main__":
    subprocess.run(["python", "generate_api_docs.py"], check=True)
    subprocess.run(["python", "swagger_yml_to_ui.py", "<", "docs.yaml", ">", "swagger.html"], check=True)
