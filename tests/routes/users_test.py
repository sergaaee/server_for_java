import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

import crud
import models
from main import app

client = TestClient(app)
endpoint = "/users"

user_data = dict(username="sergaaee", password="pp480177", email="sergoiwj@gmail.com")

mock_user = MagicMock(spec=models.Users)
mock_user.username = user_data["username"]
mock_user.email = user_data["email"]


@pytest.fixture
def setup_and_set_down_acts():
    crud.create_user = MagicMock(return_value=mock_user)
    client.post(endpoint, json=user_data)
    yield
    client.delete(endpoint, params={"email": user_data["email"]})


def test_delete_user():
    crud.create_user = MagicMock(return_value=mock_user)

    client.post(endpoint, json=user_data)

    response = client.delete(endpoint, params={"email": user_data["email"]})
    assert response.status_code == 200


def test_create_a_user():
    crud.create_user = MagicMock(return_value=mock_user)

    response = client.post(endpoint, json=user_data)
    assert response.status_code == 200

    client.delete(endpoint, params={"email": user_data["email"]})


def test_create_a_user_username_already_registered(setup_and_set_down_acts):
    user_data_2 = dict(username="sergaaee", password="pp480177", email="sergoiwj1@gmail.com")
    response = client.post(endpoint, json=user_data_2)
    assert response.text == "{\"detail\":\"Username already registered\"}"


def test_create_a_user_email_already_registered(setup_and_set_down_acts):
    user_data_2 = dict(username="sergaaeee", password="pp480177", email="sergoiwj@gmail.com")
    response = client.post(endpoint, json=user_data_2)
    assert response.text == "{\"detail\":\"Email already registered\"}"


def test_get_user_with_tasks(setup_and_set_down_acts):
    tokens = client.post("/tokens",
                         data={"username": user_data["username"], "password": user_data["password"]},
                         headers={"fingerprint": "1234", "Content-Type": "application/x-www-form-urlencoded"})

    response = client.get(endpoint, headers={"Authorization": "Bearer " + tokens.json()["access_token"]})
    assert len(response.json()) == 2
