import pytest
import requests
from lambda_forge.constants import BASE_URL


@pytest.mark.integration(method="GET", endpoint="/rag")
def test_ask_question_status_code_is_200():

    response = requests.get(url=f"{BASE_URL}/rag")

    assert response.status_code == 200
