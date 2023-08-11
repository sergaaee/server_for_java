import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

import datetime

import crud
import models
from main import app

client = TestClient(app)
endpoint = "/friend"

user_data = dict(username="sergaaee", password="pp480177", email="sergoiwj@gmail.com")
user_data_2 = dict(username="sergaaeee", password="pp480177", email="sergoiwj1@gmail.com")

mock_user_1 = MagicMock(spec=models.Users)
mock_user_1.username = user_data["username"]
mock_user_1.email = user_data["email"]

mock_user_2 = MagicMock(spec=models.Users)
mock_user_2.username = user_data["username"]
mock_user_2.email = user_data["email"]


@pytest.fixture()
def setup_and_set_down_acts():
    crud.create_user = MagicMock(return_value=mock_user_1)
    client.post("/users", json=user_data)
    crud.create_user = MagicMock(return_value=mock_user_2)
    client.post("/users", json=user_data_2)
    yield
    client.delete("/users", params={"email": user_data["email"]})
    client.delete("/users", params={"email": user_data_2["email"]})


@pytest.fixture
def get_tokens(setup_and_set_down_acts):
    token = client.post("/tokens",
                        data={"username": user_data["username"], "password": user_data["password"]},
                        headers={"fingerprint": "1234", "Content-Type": "application/x-www-form-urlencoded"}) \
        .json()["access_token"]

    token_2 = client.post("/tokens",
                          data={"username": user_data_2["username"], "password": user_data_2["password"]},
                          headers={"fingerprint": "5678", "Content-Type": "application/x-www-form-urlencoded"}) \
        .json()["access_token"]

    return dict(token=token, token_2=token_2)


def create_and_confirm_friendship(get_tokens):
    client.post(endpoint,
                json=dict(friend_id=2),
                headers={"Authorization": "Bearer " + get_tokens.get("token")}
                )

    client.patch(endpoint,
                 json=dict(friend_id=1),
                 headers={"Authorization": "Bearer " + get_tokens.get("token_2")}
                 )


def delete_friendship(get_tokens):
    client.request(method="DELETE", url=endpoint,
                   json={"friend_id": 2},
                   headers={"Authorization": "Bearer " + get_tokens.get("token")})


def test_delete_a_friend_by_id(get_tokens):
    client.post(endpoint,
                json=dict(friend_id=2),
                headers={"Authorization": "Bearer " + get_tokens.get("token")}
                )

    response = client.request(method="DELETE", url=endpoint,
                              json={"friend_id": 2},
                              headers={"Authorization": "Bearer " + get_tokens.get("token")})
    assert response.status_code == 200


def test_add_a_friend_by_id(get_tokens):
    response = client.post(endpoint,
                           json=dict(friend_id=2),
                           headers={"Authorization": "Bearer " + get_tokens.get("token")}
                           )
    assert response.status_code == 200

    delete_friendship(get_tokens)


def test_add_a_friend_by_id_not_found():
    crud.create_user = MagicMock(return_value=mock_user_1)
    client.post("/users", json=user_data)
    token = client.post("/tokens",
                        data={"username": user_data["username"], "password": user_data["password"]},
                        headers={"fingerprint": "1234", "Content-Type": "application/x-www-form-urlencoded"}) \
        .json()["access_token"]

    response = client.post(endpoint,
                           json=dict(friend_id=2),
                           headers={"Authorization": "Bearer " + token}
                           )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    client.delete("/users", params={"email": user_data["email"]})


def test_add_a_friend_connection_already_exists(get_tokens):
    create_and_confirm_friendship(get_tokens)

    response = client.post(endpoint,
                           json=dict(friend_id=2),
                           headers={"Authorization": "Bearer " + get_tokens.get("token")}
                           )
    assert response.status_code == 409
    assert response.json()["detail"] == "Connection already exists"

    delete_friendship(get_tokens)


def test_get_friend_list(get_tokens):
    client.post(endpoint,
                json=dict(friend_id=2),
                headers={"Authorization": "Bearer " + get_tokens.get("token")}
                )

    response = client.get(endpoint,
                          headers={"Authorization": "Bearer " + get_tokens.get("token")})
    assert len(response.json()) == 3
    assert response.json()[2][0].get("status") == "pending"

    delete_friendship(get_tokens)


def test_confirm_a_friend(get_tokens):
    create_and_confirm_friendship(get_tokens)

    response_for_first = client.get(endpoint,
                                    headers={"Authorization": "Bearer " + get_tokens.get("token")})
    response_for_second = client.get(endpoint,
                                     headers={"Authorization": "Bearer " + get_tokens.get("token_2")})
    assert response_for_first.json()[0][0].get("status") == "added"
    assert response_for_second.json()[0][0].get("status") == "added"

    delete_friendship(get_tokens)


def test_get_friend_tasks(get_tokens):
    create_and_confirm_friendship(get_tokens)

    response = client.get(endpoint + "/tasks",
                          headers={"Authorization": "Bearer " + get_tokens.get("token"), "friend-id": "2"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    delete_friendship(get_tokens)


def test_get_friend_tasks_not_friends(get_tokens):
    response = client.get(endpoint + "/tasks",
                          headers={"Authorization": "Bearer " + get_tokens.get("token"), "friend-id": "2"})
    assert response.status_code == 403


def test_create_a_task_with_a_friend(get_tokens):
    task_data = dict(name="test", start_time="2023-07-23 10:00:00", end_time="2023-07-23 10:00:00",
                     description="desc", status="status", created_at=str(datetime.datetime.utcnow()), sharing_from=0,
                     sharing_to=2)
    response = client.post(endpoint + "/tasks",
                           json=task_data,
                           headers={"Authorization": "Bearer " + get_tokens.get("token"), "friend-id": "2"})
    assert response.status_code == 200

    tasks = client.get("/tasks", headers={"Authorization": "Bearer " + get_tokens.get("token_2")})
    assert tasks.json()[0][0].get("name") == task_data.get("name")

    client.request(method="DELETE", url="/tasks",
                   json={"name": task_data["name"]},
                   headers={"Authorization": "Bearer " + get_tokens.get("token_2")})
    delete_friendship(get_tokens)
