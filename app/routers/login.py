# app/routes/auth_routes.py (Este código está bien)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..auth import verify_supabase_token, create_api_token
from ..schemas import BaseResponse, ErrorResponse, LoginSuccessData

import logging

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

class SupabaseLoginRequest(BaseModel):
    supabase_access_token: str

@router.post(
    "/login",
    response_model=BaseResponse[LoginSuccessData], # <-- Correcto
    responses={
        200: {"description": "Login exitoso, token de API emitido."},
        400: {"description": "Solicitud inválida o token de Supabase malformado."},
        401: {"description": "Token de Supabase inválido o expirado."},
        500: {"description": "Error interno del servidor."}
    }
)
async def login_with_supabase(request_body: SupabaseLoginRequest):
    logger.info("Recibida solicitud POST /login para verificación de token de Supabase.")
    try:
        supabase_payload = await verify_supabase_token(request_body.supabase_access_token)
        user_id_str = supabase_payload.get("sub")
        user_email = supabase_payload.get("email")

        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de Supabase no contiene un ID de usuario válido ('sub')."
            )

        api_token = create_api_token(user_id=user_id_str, email=user_email)
        logger.info(f"Login exitoso para usuario Supabase ID: {user_id_str}. Token de API personalizado emitido.")

        return BaseResponse( # <-- Correcto
            status="success",
            data=LoginSuccessData(
                access_token=api_token,
                token_type="bearer",
                user_id=user_id_str,
                email=user_email
            )
        )

    except HTTPException as e:
        logger.error(f"HTTPException en /login: {e.status_code} - {e.detail}")
        return BaseResponse( # <-- Correcto: Devuelve BaseResponse para errores HTTP
            status="error",
            error=ErrorResponse(message=e.detail, code=str(e.status_code)) # Usar str(e.status_code) como code
        )
    except Exception as e:
        logger.error(f"Error inesperado en el endpoint /login: {e}")
        return BaseResponse( # <-- Correcto: Devuelve BaseResponse para errores inesperados
            status="error",
            error=ErrorResponse(message=f"Error interno del servidor: {e}", code="SERVER_ERROR")
        )