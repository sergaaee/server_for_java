import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

import crud
import models
from main import app

client = TestClient(app)
user_data = dict(username="sergaaee", password="pp480177", email="sergoiwj@gmail.com")
mock_user = MagicMock(spec=models.Users)
mock_user.username = user_data["username"]
mock_user.email = user_data["email"]
fingerprint = "1234"
endpoint = "/tokens"

wrong_username = "wrong"
wrong_password = "wrong pass"
wrong_fingerprint = "fg"
wrong_refresh_token = "1234"


@pytest.fixture
def setup_and_set_down_acts():
    crud.create_user = MagicMock(return_value=mock_user)
    client.post("/users", json=user_data)
    yield
    client.delete("/users", params={"email": user_data["email"]})


@pytest.fixture
def auth_token(setup_and_set_down_acts):
    response = client.post("/tokens",
                           data={"username": user_data["username"], "password": user_data["password"]},
                           headers={"fingerprint": "1234", "Content-Type": "application/x-www-form-urlencoded"})
    return response.json()


def test_create_a_session(auth_token):
    assert auth_token["access_token"]
    assert auth_token["refresh_token"]


def test_refresh_all_tokens(auth_token):
    new_access_token = client.post(endpoint + "/refresh",
                                   headers={"fingerprint": fingerprint,
                                            "refresh-token": auth_token["refresh_token"]})
    assert new_access_token.json()["access_token"]


@pytest.mark.parametrize("username, password", [
    (wrong_username, user_data["password"]),
    (user_data["username"], wrong_password)
])
def test_create_a_session_wrong_data(setup_and_set_down_acts, username, password):
    response = client.post("/tokens",
                           data={"username": username, "password": password},
                           headers={"fingerprint": fingerprint, "Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401


refresh_token = None


@pytest.mark.parametrize("fingerprint, refresh_token", [
    (wrong_fingerprint, refresh_token),
    (fingerprint, wrong_refresh_token)
])
def test_refresh_all_tokens_with_wrong_data(setup_and_set_down_acts, fingerprint, refresh_token):
    if refresh_token is None:
        response = client.post("/tokens",
                               data={"username": user_data["username"], "password": user_data["password"]},
                               headers={"fingerprint": fingerprint,
                                        "Content-Type": "application/x-www-form-urlencoded"})
        auth_tokens = response.json()
        refresh_token = auth_tokens["refresh_token"]

    response = client.post(endpoint + "/refresh",
                           headers={"fingerprint": fingerprint,
                                    "refresh-token": refresh_token})
    assert response.status_code == 401
