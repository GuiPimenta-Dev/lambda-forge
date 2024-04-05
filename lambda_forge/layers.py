import shutil
import subprocess
import os

import os
from pathlib import Path
import shutil
import subprocess


import shutil
import subprocess
import os

def create_and_install_package(package_name):
    base_path = "layers"
    os.makedirs(base_path, exist_ok=True)
    base_file_path = os.path.join(base_path, '__init__.py')
    with open(base_file_path, 'w') as f:
        f.write('')

    # The package path includes the base_path and the package_name
    package_path = os.path.join(base_path, package_name)

    # Normalize package directory path
    package_path = os.path.normpath(package_path)

    # Ensure the package directory exists
    os.makedirs(package_path, exist_ok=True)

    # Create __init__.py to make it a Python package
    init_file_path = os.path.join(package_path, '__init__.py')
    with open(init_file_path, 'w') as f:
        f.write(f'from .{package_name} import *\n')
    
    layer_file_path = os.path.join(package_path, f'{package_name}.py')
    with open(layer_file_path, 'w') as f:
        f.write(f"""def hello_from_layer():
    print("Hello from {package_name} layer!")
""")

    # Create setup.py specific to this package
    with open(base_path + "/setup.py", 'w') as f:
        f.write(f"""
from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1",
    packages=find_packages(),
)
""")

    # Install the package into the virtual environment using its setup.py
    try:
        # Execute the subprocess, capturing stdout and stderr
        result = subprocess.run(['pip', 'install', '-e', base_path], 
                                check=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                text=True)  # Ensure output is in text format, not bytes
        # If the subprocess does not raise an error, print its output (if any)
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        # Print the error message and the stderr from the subprocess, if it fails
        print("Error:", e)
        print("Error Output:", e.stderr)

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
            if dirname.endswith('egg-info'):
                full_path = Path(dirpath) / dirname
                shutil.rmtree(full_path)

def _install_package_and_cleanup(layer, base_path):
    """Create setup.py, install package, and cleanup for a given layer."""
    setup_path = Path(base_path) / 'setup.py'
    with setup_path.open('w') as f:
        f.write(f"""
from setuptools import setup, find_packages

setup(
    name="{layer.name}",
    version="0.1",
    packages=find_packages(),
)
    """)

    try:
        # Execute the subprocess, capturing stdout and stderr
        result = subprocess.run(['pip', 'install', '-e', base_path], 
                                check=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                text=True)  # Ensure output is in text format, not bytes
        # If the subprocess does not raise an error, print its output (if any)
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        # Print the error message and the stderr from the subprocess, if it fails
        print("Error:", e)
        print("Error Output:", e.stderr)
    
    setup_path.unlink()


def install_all_layers():
    base_path = 'layers'

    for layer in _list_subfolders(base_path):
        _install_package_and_cleanup(layer, base_path)
        _remove_egg_info_directories(base_path)

create_and_install_package("pkg")