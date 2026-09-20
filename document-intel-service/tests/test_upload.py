import io
import pytest


@pytest.fixture
def auth_headers(client):
    client.post(
        "/auth/register",
        json={"email": "uploader@example.com", "password": "password123"}
    )
    res = client.post(
        "/auth/login",
        json={"email": "uploader@example.com", "password": "password123"}
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def secondary_auth_headers(client):
    client.post(
        "/auth/register",
        json={"email": "otheruser@example.com", "password": "password123"}
    )
    res = client.post(
        "/auth/login",
        json={"email": "otheruser@example.com", "password": "password123"}
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_success_pdf(client, auth_headers):
    file_content = b"%PDF-1.4 sample pdf content header"
    files = {"file": ("test_paper.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"doc_type": "question_paper"}
    
    response = client.post("/documents/upload", files=files, data=data, headers=auth_headers)
    assert response.status_code == 202
    resp_data = response.json()
    assert "document_id" in resp_data
    assert resp_data["filename"] == "test_paper.pdf"

    # Verify status transition & metadata
    doc_id = resp_data["document_id"]
    doc_res = client.get(f"/documents/{doc_id}", headers=auth_headers)
    assert doc_res.status_code == 200
    assert doc_res.json()["status"] in ["completed", "processing", "pending"]


def test_upload_invalid_file_type(client, auth_headers):
    file_content = b"Some plain text content"
    files = {"file": ("malicious.txt", io.BytesIO(file_content), "text/plain")}
    
    response = client.post("/documents/upload", files=files, headers=auth_headers)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_upload_oversized_file(client, auth_headers, monkeypatch):
    from app.config import settings
    # Temporarily set max upload size to 1 MB for testing
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)
    
    # 2 MB content
    large_content = b"0" * (2 * 1024 * 1024)
    files = {"file": ("large_file.pdf", io.BytesIO(large_content), "application/pdf")}
    
    response = client.post("/documents/upload", files=files, headers=auth_headers)
    assert response.status_code == 413
    assert "exceeds maximum limit" in response.json()["detail"]


def test_unauthorized_document_access(client, auth_headers, secondary_auth_headers):
    # User 1 uploads document
    file_content = b"%PDF-1.4 sample pdf"
    files = {"file": ("user1_paper.pdf", io.BytesIO(file_content), "application/pdf")}
    upload_res = client.post("/documents/upload", files=files, headers=auth_headers)
    doc_id = upload_res.json()["document_id"]

    # User 2 attempts to fetch User 1's document
    res = client.get(f"/documents/{doc_id}", headers=secondary_auth_headers)
    assert res.status_code == 404

    # User 2 attempts to delete User 1's document
    del_res = client.delete(f"/documents/{doc_id}", headers=secondary_auth_headers)
    assert del_res.status_code == 404


def test_get_documents_list(client, auth_headers):
    response = client.get("/documents", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
