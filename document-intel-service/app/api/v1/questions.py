from fastapi import APIRouter

router = APIRouter()


@router.get("")
def get_questions():
    return []


@router.get("/{question_id}")
def get_question(question_id: int):
    return {"id": question_id, "message": "Get question stub"}
