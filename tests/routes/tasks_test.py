import datetime

import pytest

from fastapi.testclient import TestClient
from unittest.mock import MagicMock

import crud
import models
from main import app

client = TestClient(app)
endpoint = "/tasks"

user_data = dict(username="sergaaee", password="pp480177", email="sergoiwj@gmail.com")
mock_user = MagicMock(spec=models.Users)
mock_user.username = user_data["username"]
mock_user.email = user_data["email"]

task_data = dict(name="test", start_time=str(datetime.datetime.utcnow()), end_time=str(datetime.datetime.utcnow()),
                 description="desc", status="some status", created_at=str(datetime.datetime.utcnow()), sharing_from=0,
                 sharing_to=1)
mock_task = MagicMock(spec=models.Tasks)


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
    return response.json()["access_token"]


def test_delete_a_task(auth_token):
    client.post(endpoint,
                json=task_data,
                headers={"Authorization": "Bearer " + auth_token})

    response = client.request(method="DELETE", url=endpoint,
                              json={"name": task_data["name"]},
                              headers={"Authorization": "Bearer " + auth_token})
    assert response.status_code == 200


def test_create_a_task(auth_token):
    response = client.post(endpoint,
                           json=task_data,
                           headers={"Authorization": "Bearer " + auth_token})
    assert response.status_code == 200

    client.request(method="DELETE", url=endpoint,
                   json={"name": task_data["name"]},
                   headers={"Authorization": "Bearer " + auth_token})


def test_get_all_tasks(auth_token):
    response = client.get(endpoint, headers={"Authorization": "Bearer " + auth_token})
    assert len(response.json()) == 1

    client.request(method="DELETE", url=endpoint,
                   json={"name": task_data["name"]},
                   headers={"Authorization": "Bearer " + auth_token})


def test_update_task_name():
    pass
