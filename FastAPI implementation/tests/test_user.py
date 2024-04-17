from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_user(db):
    data = {
        "username": "test",
        "email": "test@gmail.com",
        "password": "test",
        "is_active": True
    }
    response = client.post("/user", json=data)
    result = response.json()
    assert response.status_code == 200
    assert result['username'] == data['username']
    assert result['email'] == data['email']
    assert result['is_active'] == data['is_active']
    second_response = client.post("/user", json=data)
    assert second_response.status_code == 400


def get_token():
    data = {
        "username": "test",
        "password": "test",
        "scopes": '["me", "user:read", "admin:read"]'
    }
    response = client.post("/token", data=data)
    result = response.json()
    print(result)
    return result['access_token']


def test_login(db):
    data = {
        "username": "test",
        "password": "test",
        "scopes": ["me", "user:read", "admin:read"]
    }
    response = client.post("/token", data=data)
    result = response.json()
    assert response.status_code == 200
    assert result['username'] == data['username']


def test_get_all_users(db):
    token = get_token()
    response = client.get("/user/all", headers={"Authorization": f"Bearer {token}"})
    result = response.json()
    print(result)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_user(db):
    data = {
        "username": "test_updated",
        "email": "test_updated@gmail.com",
        "password": "test_updated",
        "is_active": True
    }
    token = get_token()
    response = client.put("/user/me", json=data, headers={"Authorization": f"Bearer {token}"})
    result = response.json()
    assert response.status_code == 200
    assert result['username'] == data['username']
    assert result['email'] == data['email']
    assert result['is_active'] == data['is_active']
