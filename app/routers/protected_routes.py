from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter()

@router.get("/profile")
def get_profile(user=Depends(get_current_user)):
    return {"message": "Bienvenido", "user": user}
