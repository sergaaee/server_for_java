import json

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


def test_create_a_user():
    crud.create_user = MagicMock(return_value=mock_user)

    response = client.post("/users", json=user_data)
    assert response.status_code == 200

    client.delete("/users", params={"email": user_data["email"]})


def test_create_a_user_username_already_registered():
    crud.create_user = MagicMock(return_value=mock_user)

    client.post("/users", json=user_data)

    user_data_2 = dict(username="sergaaee", password="pp480177", email="sergoiwj1@gmail.com")
    response = client.post("/users", json=user_data_2)
    assert response.text == "{\"detail\":\"Username already registered\"}"

    client.delete("/users", params={"email": user_data["email"]})


def test_create_a_user_email_already_registered():
    crud.create_user = MagicMock(return_value=mock_user)

    client.post("/users", json=user_data)

    user_data_2 = dict(username="sergaaeee", password="pp480177", email="sergoiwj@gmail.com")
    response = client.post("/users", json=user_data_2)
    assert response.text == "{\"detail\":\"Email already registered\"}"

    client.delete("/users", params={"email": user_data["email"]})


def test_delete_user():
    crud.create_user = MagicMock(return_value=mock_user)

    client.post("/users", json=user_data)

    response = client.delete("/users", params={"email": user_data["email"]})
    assert response.status_code == 200


def test_get_user_with_tasks():
    crud.create_user = MagicMock(return_value=mock_user)

    client.post("/users", json=user_data)
    token = client.post("/tokens",
                        data={"username": user_data["username"], "password": user_data["password"]},
                        headers={"fingerprint": "1234", "Content-Type": "application/x-www-form-urlencoded"})

    response = client.get("/users", headers={"Authorization": "Bearer " + token.json()["access_token"]})
    assert len(response.json()) == 2

    client.delete("/users", params={"email": user_data["email"]})
