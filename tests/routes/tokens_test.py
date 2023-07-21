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


def test_create_a_session():
    crud.create_user = MagicMock(return_value=mock_user)

    client.post("/users", json=user_data)

    tokens = client.post(endpoint,
                         data={"username": user_data["username"], "password": user_data["password"]},
                         headers={"fingerprint": fingerprint, "Content-Type": "application/x-www-form-urlencoded"})
    assert tokens.json()["access_token"]
    assert tokens.json()["refresh_token"]

    client.delete("/users", params={"email": user_data["email"]})


def test_refresh_all_tokens():
    crud.create_user = MagicMock(return_value=mock_user)

    client.post("/users", json=user_data)

    tokens = client.post(endpoint,
                         data={"username": user_data["username"], "password": user_data["password"]},
                         headers={"fingerprint": fingerprint, "Content-Type": "application/x-www-form-urlencoded"})

    new_access_token = client.post(endpoint + "/refresh",
                                   headers={"fingerprint": fingerprint,
                                            "refresh-token": tokens.json()["refresh_token"]})
    assert new_access_token.json()["access_token"]

    client.delete("/users", params={"email": user_data["email"]})
