def test_registration_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data


def test_registration_duplicate_email(client):
    client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "loginuser@example.com", "password": "secretpassword"}
    )
    response = client.post(
        "/auth/login",
        json={"email": "loginuser@example.com", "password": "secretpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
