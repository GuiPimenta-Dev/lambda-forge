import subprocess

if __name__ == "__main__":
    subprocess.run(["python", "generate_api_docs.py"], check=True)
    with open("docs.yaml", "r") as input_file:
        with open("swagger.html", "w") as output_file:
            subprocess.run(["python", "swagger_yml_to_ui.py"], stdin=input_file, stdout=output_file, check=True)
