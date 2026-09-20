def test_auth_stub(client):
    response = client.post("/auth/login")
    assert response.status_code == 200
    assert response.json()["message"] == "Login endpoint stub"
