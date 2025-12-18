import pytest
import bcrypt
from flask_jwt_extended import create_access_token
from application import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def access_token():
    with app.app_context():
        return create_access_token(identity="testuser")



@pytest.fixture
def auth_header(access_token):
    return {
        "Authorization": f"Bearer {access_token}"
    }

def test_migracion(client, mock_db):
    res = client.get("/flask/migracion")
    assert res.status_code == 200

def test_root(client):
    response = client.get("/flask/")
    assert response.status_code == 200
    assert b"Hello, World SOY MANTECA LO HICE AL FIN YAAAAAAAAAAAAA!" in response.data


def test_register_ok(client, mock_db):
    payload = {
        "username": "testuser",
        "password": "1234",
        "name": "Test",
        "lastname": "User",
        "email": "test@test.com",
        "phone": "123456789",
        "date": "25/12/2025"
    }

    response = client.post("/flask/register", json=payload)
    assert response.status_code == 200
    assert response.json["msg"] == "user created"


def test_login_ok(client, mock_db):
    mock_db["usuarios"].find_one.return_value = {
        "username": "testuser",
        "password": "$2b$12$abcdefghijklmnopqrstuv"
    }

    import bcrypt
    bcrypt.checkpw = lambda pwd, hashed: True

    response = client.post("/flask/login", json={
        "username": "testuser",
        "password": "1234"
    })

    assert response.status_code == 200
    assert "access_token" in response.json

def test_profile_ok(client, auth_header, mock_db):
    mock_db["usuarios"].find_one = lambda q, p: {
        "username": "testuser",
        "name": "Test",
        "lastname": "User"
    }

    res = client.get("/flask/profile", headers=auth_header)

    assert res.status_code == 200
    assert res.json["username"] == "testuser"

def test_centers_ok(client, auth_header, mock_db):
    mock_db["centros"].find = lambda q, p: [
        {"name": "Centro Norte", "address": "Madrid"}
    ]

    res = client.get("/flask/centers", headers=auth_header)

    assert res.status_code == 200
    assert isinstance(res.json, list)

def test_create_date_ok(client, auth_header, mock_db):
    mock_db["centros"].find_one = lambda q: {"name": q["name"]}
    mock_db["citas"].find_one = lambda q: None

    res = client.post(
        "/flask/date/create",
        headers=auth_header,
        json={
            "center": "Centro Norte",
            "date": "25/12/2025 14:00:00"
        }
    )

    assert res.status_code == 200
    assert res.json["msg"] == "Date created successfully"

def test_get_dates_by_user(client, auth_header, mock_db):
    mock_db["citas"].find = lambda q, p: [
        {"day": "25/12/2025", "hour": "14", "username": "testuser"}
    ]

    res = client.get("/flask/date/getByUser", headers=auth_header)

    assert res.status_code == 200
    assert len(res.json) == 1


def test_get_dates_by_day(client, auth_header, mock_db):
    mock_db["citas"].find = lambda q, p: [
        {"day": "25/12/2025", "hour": "14"}
    ]

    res = client.post(
        "/flask/date/getByDay",
        headers=auth_header,
        json={"day": "25/12/2025"}
    )

    assert res.status_code == 200
    assert isinstance(res.json, list)

def test_delete_date_ok(client, auth_header, mock_db):
    mock_db["citas"].find_one = lambda q: {
        "day": "25/12/2025",
        "hour": "14",
        "center": "Centro Norte",
        "username": "testuser"
    }

    res = client.post(
        "/flask/date/delete",
        headers=auth_header,
        json={
            "center": "Centro Norte",
            "date": "25/12/2025 14:00:00"
        }
    )

    assert res.status_code == 200
    assert res.json["msg"] == "Date deleted successfully"


def test_get_all_dates(client, auth_header, mock_db):
    mock_db["citas"].find = lambda q, p: []

    res = client.get("/flask/dates", headers=auth_header)
    assert res.status_code == 200