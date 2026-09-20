import pytest


@pytest.fixture
def auth_headers(client):
    client.post(
        "/auth/register",
        json={"email": "groupuser@example.com", "password": "password123"}
    )
    res = client.post(
        "/auth/login",
        json={"email": "groupuser@example.com", "password": "password123"}
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_document_group_flow(client, auth_headers):
    # 1. Create document group
    grp_res = client.post(
        "/document-groups",
        json={"name": "Computer Science Exam Group"},
        headers=auth_headers
    )
    assert grp_res.status_code == 201
    group_id = grp_res.json()["id"]

    # 2. Upload question paper to group
    with open("sample_documents/clean_question_paper.pdf", "rb") as f:
        files = {"file": ("clean_paper.pdf", f, "application/pdf")}
        data = {"doc_type": "question_paper", "group_id": group_id}
        qp_res = client.post("/documents/upload", files=files, data=data, headers=auth_headers)
        assert qp_res.status_code == 202

    # 3. Upload answer key to group
    with open("sample_documents/answer_key.pdf", "rb") as f:
        files_ak = {"file": ("answer_key.pdf", f, "application/pdf")}
        data_ak = {"doc_type": "answer_key", "group_id": group_id}
        ak_res = client.post("/documents/upload", files=files_ak, data=data_ak, headers=auth_headers)
        assert ak_res.status_code == 202

    # 4. Fetch group details
    group_fetch = client.get(f"/document-groups/{group_id}", headers=auth_headers)
    assert group_fetch.status_code == 200
    grp_data = group_fetch.json()
    assert len(grp_data["documents"]) == 2

    # 5. Fetch questions and associated answer
    q_res = client.get("/questions", headers=auth_headers)
    assert q_res.status_code == 200
    questions = q_res.json()
    assert len(questions) > 0

    # Fetch answer for Q1
    q1 = [q for q in questions if q.get("question_number") == "Q1"][0]
    ans_res = client.get(f"/questions/{q1['id']}/answer", headers=auth_headers)
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["status"] == "matched"
    assert ans_data["match_confidence"] >= 0.90
