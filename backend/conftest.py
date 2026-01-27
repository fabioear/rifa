import pytest
import requests

BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture(scope="module")
def token():
    response = requests.post(
        f"{BASE_URL}/login/access-token",
        data={"username": "admin@example.com", "password": "admin"},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    pytest.fail(f"Login Failed: {response.text}")


@pytest.fixture(scope="module")
def rifa_id(token):
    headers = {"Authorization": f"Bearer {token}"}
    rifas = requests.get(f"{BASE_URL}/rifas/", headers=headers).json()
    if rifas:
        return rifas[0]["id"]
    pytest.fail("No rifas found")

