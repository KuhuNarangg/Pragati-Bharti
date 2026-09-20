import io
import pytest


@pytest.fixture
def auth_headers(client):
    client.post(
        "/auth/register",
        json={"email": "q_user@example.com", "password": "password123"}
    )
    res = client.post(
        "/auth/login",
        json={"email": "q_user@example.com", "password": "password123"}
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_question_retrieval(client, auth_headers):
    # Upload document to trigger extraction
    with open("sample_documents/clean_question_paper.pdf", "rb") as f:
        files = {"file": ("clean_paper.pdf", f, "application/pdf")}
        upload_res = client.post("/documents/upload", files=files, headers=auth_headers)
        assert upload_res.status_code == 202
        doc_id = upload_res.json()["document_id"]

    # Retrieve questions for document
    q_res = client.get(f"/questions?document_id={doc_id}", headers=auth_headers)
    assert q_res.status_code == 200
    questions = q_res.json()
    assert len(questions) >= 3

    # Retrieve single question
    q1_id = questions[0]["id"]
    q_single = client.get(f"/questions/{q1_id}", headers=auth_headers)
    assert q_single.status_code == 200
    assert q_single.json()["id"] == q1_id
