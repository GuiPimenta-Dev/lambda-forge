import pytest
from lambda_forge import layers
from tests.conftest import list_files

@pytest.mark.skip(reason="slow")
def test_create_and_install_package():
  package_name = "pkg"

  layers.create_and_install_package(package_name)

  files = list_files("layers")
  
  assert f"layers/{package_name}/__init__.py" in files

@pytest.mark.skip(reason="slow")
def test_install_all_packages():
  package_name = "pkg"

  layers.create_and_install_package(package_name)
  layers.install_all_packages()

  files = list_files("layers")
  
  assert f"layers/{package_name}/__init__.py" in files
