def test_upload_stub(client):
    response = client.post("/documents/upload")
    assert response.status_code == 200
    assert response.json()["message"] == "Upload document stub"
