import pytest


@pytest.fixture
def auth_headers(client):
    client.post(
        "/auth/register",
        json={"email": "reviewuser@example.com", "password": "password123"}
    )
    res = client.post(
        "/auth/login",
        json={"email": "reviewuser@example.com", "password": "password123"}
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_review_items_endpoint(client, auth_headers):
    # Upload low quality scanned document to generate review items
    with open("sample_documents/scanned_low_quality.jpg", "rb") as f:
        files = {"file": ("scanned_paper.jpg", f, "image/jpeg")}
        upload_res = client.post("/documents/upload", files=files, headers=auth_headers)
        assert upload_res.status_code == 202

    # Fetch review items
    res = client.get("/review-items", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_review_items" in data
    assert "items" in data
    assert isinstance(data["items"], list)
