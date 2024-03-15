import re
import subprocess

def read_version():
    """Reads the version from setup.py."""
    with open("setup.py", "r") as file:
        content = file.read()
        version_match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
        if version_match:
            return version_match.group(1)
    return None

def increment_version(version):
    """Increments the patch number in the version."""
    major, minor, patch = map(int, version.split('.'))
    return f"{major}.{minor}.{patch + 1}"

def update_setup_py(new_version):
    """Updates the setup.py file with the new version."""
    with open("setup.py", "r") as file:
        content = file.read()
    content = re.sub(r"(version=['\"])([^'\"]+)(['\"])", fr"\g<1>{new_version}\3", content)
    with open("setup.py", "w") as file:
        file.write(content)

def build_and_upload():
    """Builds the package and uploads it to TestPyPI."""
    subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"], check=True)
    subprocess.run(["twine", "upload", "--repository", "testpypi", "dist/*"], check=True)

def main():
    current_version = read_version()
    if current_version is None:
        raise Exception("Could not read the current version from setup.py.")
    new_version = increment_version(current_version)
    print(f"Updating version: {current_version} -> {new_version}")
    update_setup_py(new_version)
    print("Building and uploading the package to TestPyPI...")
    build_and_upload()
    print("Done.")

if __name__ == "__main__":
    main()
