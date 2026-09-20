from fastapi import APIRouter

router = APIRouter()


@router.get("/{question_id}/answer")
def get_question_answer(question_id: int):
    return {"question_id": question_id, "message": "Get answer stub"}
