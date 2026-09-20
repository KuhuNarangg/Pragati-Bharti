from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
def upload_document():
    return {"message": "Upload document stub"}


@router.get("")
def get_documents():
    return []


@router.get("/{document_id}")
def get_document(document_id: int):
    return {"id": document_id, "message": "Get document stub"}


@router.get("/{document_id}/status")
def get_document_status(document_id: int):
    return {"id": document_id, "status": "pending"}


@router.delete("/{document_id}")
def delete_document(document_id: int):
    return {"message": f"Document {document_id} deleted"}
