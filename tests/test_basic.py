from application import app


def test_root(client):
    response = client.get("/flask")
    assert response.status_code == 200
    assert b"Hello, World!" in response.data


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
    # simulamos usuario con contraseña correcta
    mock_db["usuarios"].find_one.return_value = {
        "username": "testuser",
        "password": "$2b$12$abcdefghijklmnopqrstuv"
    }

    # forzar bcrypt.checkpw = True
    import bcrypt
    bcrypt.checkpw = lambda pwd, hashed: True

    response = client.post("/flask/login", json={
        "username": "testuser",
        "password": "1234"
    })

    assert response.status_code == 200
    assert "access_token" in response.json
