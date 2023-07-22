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

wrong_password = "1234"
wrong_username = "wro"
wrong_email = "1234"


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


def test_get_user_with_tasks_wrong_token(setup_and_set_down_acts):
    fake_token = "1234"

    response = client.get(endpoint, headers={"Authorization": "Bearer " + fake_token})
    assert response.status_code == 401


@pytest.mark.parametrize("username, password, email", [
    (wrong_username, user_data["password"], user_data["email"]),
    (user_data["username"], wrong_password, user_data["email"]),
    (user_data["username"], user_data["password"], wrong_email)
])
def test_create_a_user_wrong_data(username, password, email):
    response = client.post(endpoint, json=dict(username=username, password=password, email=email))
    assert response.status_code == 422
