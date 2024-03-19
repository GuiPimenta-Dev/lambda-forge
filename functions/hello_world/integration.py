import pytest
import requests

@pytest.mark.integration(method="GET", endpoint="/hello_world")
def test_hello_world_status_code_is_200():

    response = requests.get(url="")

    assert response.status_code == 200 
