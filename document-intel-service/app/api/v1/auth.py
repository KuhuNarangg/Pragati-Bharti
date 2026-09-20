from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
def register():
    return {"message": "Registration endpoint stub"}


@router.post("/login")
def login():
    return {"message": "Login endpoint stub"}
