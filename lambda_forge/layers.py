import importlib.metadata
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

import boto3

from lambda_forge.printer import Printer


def create_and_install_package(package_name):
    base_path = "layers"
    os.makedirs(base_path, exist_ok=True)
    base_file_path = os.path.join(base_path, "__init__.py")
    with open(base_file_path, "w") as f:
        f.write("")

    # The package path includes the base_path and the package_name
    package_path = os.path.join(base_path, package_name)

    # Normalize package directory path
    package_path = os.path.normpath(package_path)

    # Ensure the package directory exists
    os.makedirs(package_path, exist_ok=True)

    # Create __init__.py to make it a Python package
    init_file_path = os.path.join(package_path, "__init__.py")
    with open(init_file_path, "w") as f:
        f.write(f"from .{package_name} import *\n")

    layer_file_path = os.path.join(package_path, f"{package_name}.py")
    with open(layer_file_path, "w") as f:
        f.write(
            f"""def hello_from_layer():
    return "Hello from {package_name} layer!"
"""
        )

    # Create setup.py specific to this package
    with open(base_path + "/setup.py", "w") as f:
        f.write(
            f"""
from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1",
    packages=find_packages(),
)
"""
        )

    # Install the package into the virtual environment using its setup.py
    try:
        # Execute the subprocess, capturing stdout and stderr
        subprocess.run(
            ["pip", "install", "-e", base_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )  # Ensure output is in text format, not bytes
    except subprocess.CalledProcessError as e:
        # Print the error message and the stderr from the subprocess, if it fails
        pass

    # Cleanup: Remove the .egg-info directory created by setuptools
    egg_info_path = os.path.join("layers", f"{package_name}.egg-info")
    if os.path.exists(egg_info_path):
        shutil.rmtree(egg_info_path)
    os.remove("layers/setup.py")


def _list_subfolders(directory):
    """List all subfolders in the given directory using pathlib."""
    return [entry for entry in Path(directory).iterdir() if entry.is_dir()]


def _remove_egg_info_directories(base_path):
    """Remove all directories ending with 'egg-info' within the base_path."""
    for dirpath, dirnames, filenames in os.walk(base_path, topdown=False):
        for dirname in dirnames:
            if dirname.endswith("egg-info"):
                full_path = Path(dirpath) / dirname
                shutil.rmtree(full_path)


def _install_package_and_cleanup(layer, base_path):
    """Create setup.py, install package, and cleanup for a given layer."""
    setup_path = Path(base_path) / "setup.py"
    with setup_path.open("w") as f:
        f.write(
            f"""
from setuptools import setup, find_packages

setup(
    name="{layer.name}",
    version="0.1",
    packages=find_packages(),
)
    """
        )

        # Execute the subprocess, capturing stdout and stderr
    subprocess.run(
        ["pip", "install", "-e", base_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )  # Ensure output is in text format, not bytes

    setup_path.unlink()


def install_all_layers():
    base_path = "layers"

    if not os.path.exists(base_path):
        print("No layers to install.")
        return

    for layer in _list_subfolders(base_path):
        _install_package_and_cleanup(layer, base_path)
        _remove_egg_info_directories(base_path)


def deploy_external_layer(lib, region):

    # Get the path to the system's temporary directory
    temp_dir = tempfile.gettempdir()

    # Combine the temporary directory path with your folder name
    folder_path = os.path.join(temp_dir, lib)

    # Create the folder
    os.makedirs(folder_path, exist_ok=True)

    lib_dir = folder_path + "/python"
    os.makedirs(lib_dir, exist_ok=True)

    current_dir = os.getcwd()

    os.chdir(lib_dir)

    subprocess.run(["pip", "install", lib, "-t", "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    dist_info_dirs = [d for d in os.listdir(".") if d.endswith(".dist-info")]
    for d in dist_info_dirs:
        shutil.rmtree(d)

    os.chdir(folder_path)

    lib_zip = f"{lib}.zip"
    subprocess.run(["zip", "-r", lib_zip, "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    s3_client = boto3.client("s3", region_name=region)

    bucket_name = f"{lib}-layer-" + str(uuid.uuid4())

    existing_buckets = s3_client.list_buckets()["Buckets"]
    bucket = None
    for existing_bucket in existing_buckets:
        name = existing_bucket["Name"]
        if f"{lib}-layer-" in name:
            bucket = existing_bucket
            break

    if not bucket:
        bucket = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": region})

    s3_client.upload_file(lib_zip, bucket["Name"], lib_zip)

    lambda_client = boto3.client("lambda", region_name=region)

    response = lambda_client.publish_layer_version(
        LayerName=lib,
        Content={"S3Bucket": bucket["Name"], "S3Key": lib_zip},
    )
    arn = response["LayerVersionArn"]
    os.chdir(current_dir)
    return arn


def install_external_layer(library_name):
    # Install the library using pip
    subprocess.run(["pip", "install", library_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Get the installed version of the library
    installed_version = importlib.metadata.version(library_name)

    return installed_version


def update_requirements_txt(requirements_file, library):
    printer = Printer()
    try:
        if library in open(requirements_file).read():
            return

        with open(requirements_file, "a") as file:
            file.write(f"\n{library}")
    except Exception as e:
        printer.print(f"Error occurred: {str(e)}", "red")
