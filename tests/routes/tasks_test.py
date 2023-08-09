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

task_data = dict(name="test", start_time="2023-07-23 10:00:00", end_time="2023-07-23 10:00:00",
                 description="desc", status="status", created_at=str(datetime.datetime.utcnow()), sharing_from=0,
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


def delete_task(auth_token):
    client.request(method="DELETE", url=endpoint,
                   json={"name": task_data["name"]},
                   headers={"Authorization": "Bearer " + auth_token})


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

    tasks = client.get("/tasks", headers={"Authorization": "Bearer " + auth_token})
    assert tasks.json()[0][0].get("name") == task_data.get("name")

    delete_task(auth_token)


def test_get_all_tasks(auth_token):
    response = client.get(endpoint, headers={"Authorization": "Bearer " + auth_token})
    assert len(response.json()) == 1


@pytest.mark.parametrize("new_name, new_stime, new_etime, new_desc, new_status", [
    ("new name", task_data["start_time"], task_data["end_time"], task_data["description"], task_data["status"]),
    (task_data["name"], "2023-07-23 11:00:00", task_data["end_time"], task_data["description"], task_data["status"]),
    (task_data["name"], task_data["start_time"], "2023-07-23 10:30:00", task_data["description"], task_data["status"]),
    (task_data["name"], task_data["start_time"], task_data["end_time"], "new desc", task_data["status"]),
    (task_data["name"], task_data["start_time"], task_data["end_time"], task_data["description"], "new status")
])
def test_update_task(auth_token, new_name, new_stime, new_etime, new_desc, new_status):
    client.post(endpoint,
                json=task_data,
                headers={"Authorization": "Bearer " + auth_token})

    response = client.patch(endpoint,
                            json=dict(name=task_data["name"],
                                      new_name=new_name,
                                      new_stime=new_stime,
                                      new_etime=new_etime,
                                      new_desc=new_desc,
                                      new_status=new_status),
                            headers={"Authorization": "Bearer " + auth_token})
    assert response.status_code == 200

    client.request(method="DELETE", url=endpoint,
                   json={"name": new_name},
                   headers={"Authorization": "Bearer " + auth_token})


@pytest.mark.parametrize("new_stime, new_etime", [
    (123, task_data["end_time"]),
    (task_data["start_time"], 123),
])
def test_update_task_wrong_datetime_format(auth_token, new_stime, new_etime):
    client.post(endpoint,
                json=task_data,
                headers={"Authorization": "Bearer " + auth_token})

    response = client.patch(endpoint,
                            json=dict(name=task_data["name"],
                                      new_name=task_data["name"],
                                      new_stime=new_stime,
                                      new_etime=new_etime,
                                      new_desc=task_data["description"],
                                      new_status=task_data["status"]),
                            headers={"Authorization": "Bearer " + auth_token})
    assert response.status_code == 422

    delete_task(auth_token)


@pytest.mark.parametrize("start_time, end_time", [
    (123, task_data["end_time"]),
    (task_data["start_time"], 123)
])
def test_create_a_task_wrong_data(auth_token, start_time, end_time):
    temp_task_data = task_data.copy()
    temp_task_data["start_time"] = start_time
    temp_task_data["end_time"] = end_time
    response = client.post(endpoint,
                           json=temp_task_data,
                           headers={"Authorization": "Bearer " + auth_token})
    assert response.status_code == 422


def test_create_a_task_name_already_exists(auth_token):
    client.post(endpoint,
                json=task_data,
                headers={"Authorization": "Bearer " + auth_token})

    response = client.post(endpoint,
                           json=task_data,
                           headers={"Authorization": "Bearer " + auth_token})
    assert response.status_code == 409

    delete_task(auth_token)


def test_delete_a_task_wrong_name(auth_token):
    response = client.request(method="DELETE", url=endpoint,
                              json={"name": task_data["name"]},
                              headers={"Authorization": "Bearer " + auth_token})
    assert response.status_code == 404
