import pytest
import requests
from lambda_forge.constants import BASE_URL


@pytest.mark.integration(method="GET", endpoint="/custom")
def test_using_custom_layer_status_code_is_200():

    response = requests.get(url=f"{BASE_URL}/custom")

    assert response.status_code == 200
