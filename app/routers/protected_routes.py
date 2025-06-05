from fastapi import APIRouter, Depends
from app.auth import get_current_user_from_api_token

router = APIRouter()

@router.get("/profile")
def get_profile(user=Depends(get_current_user_from_api_token)): # <--- To this!
    return {"message": "Bienvenido", "user": user}