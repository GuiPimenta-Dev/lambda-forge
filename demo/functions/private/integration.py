import pytest
import requests
from lambda_forge.constants import BASE_URL


@pytest.mark.integration(method="GET", endpoint="/private")
def test_private_status_code_with_no_header_is_403():

    response = requests.get(url=f"{BASE_URL}/private")

    assert response.status_code == 403


@pytest.mark.integration(method="GET", endpoint="/private")
def test_private_status_code_with_valid_header_is_200():

    headers = {"secret": "CRMdDRMA4iW4xo9l38pACls7zsHYfp8T7TLXtucysb2lB5XBVFn8"}

    response = requests.get(url=f"{BASE_URL}/private", headers=headers)

    assert response.status_code == 200
