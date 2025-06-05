from pydantic import BaseModel, UUID4
from typing import Optional, TypeVar, Generic, List

T = TypeVar("T")

class ErrorResponse(BaseModel):
    # Aquí, 'code' estaba como 'str' en tu ejemplo, pero puede ser opcional
    # si no siempre envías un código.
    code: Optional[str] # Cambiado a Optional[str] para mayor flexibilidad
    message: str

class BaseResponse(BaseModel, Generic[T]):
    status: str  # "success" o "error"
    data: Optional[T] = None # Siempre inicialízalo a None
    error: Optional[ErrorResponse] = None # Siempre inicialízalo a None

class LoginSuccessData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: Optional[str] = None