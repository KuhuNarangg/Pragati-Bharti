from fastapi import APIRouter

router = APIRouter()


@router.post("")
def create_document_group():
    return {"message": "Create document group stub"}


@router.get("/{group_id}")
def get_document_group(group_id: int):
    return {"id": group_id, "message": "Get document group stub"}
