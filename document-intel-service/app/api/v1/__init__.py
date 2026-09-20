from fastapi import APIRouter
from app.api.v1 import auth, documents, groups, questions, answers, review

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(groups.router, prefix="/document-groups", tags=["document-groups"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(answers.router, prefix="/questions", tags=["answers"])
api_router.include_router(review.router, prefix="/review-items", tags=["review"])
