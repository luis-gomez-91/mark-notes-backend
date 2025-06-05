from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
import base64

security = HTTPBearer()

SUPABASE_JWT_SECRET_BASE64 = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_JWT_ALGORITHM = "HS256"

SUPABASE_JWT_SECRET_DECODED = None
try:
    if SUPABASE_JWT_SECRET_BASE64 is None:
        print("ERROR: SUPABASE_JWT_SECRET no está configurado (es None).")
        # Podrías lanzar un error aquí para evitar que la app inicie sin secreto
        raise ValueError("SUPABASE_JWT_SECRET no está configurado en las variables de entorno.")

    # Imprimir el secreto Base64 antes de decodificar
    print(f"DEBUG: SUPABASE_JWT_SECRET_BASE64 (desde .env): '{SUPABASE_JWT_SECRET_BASE64}'")

    # Decodificar el secreto de Base64 a bytes
    SUPABASE_JWT_SECRET_DECODED = base64.b64decode(SUPABASE_JWT_SECRET_BASE64)

    # Imprimir el secreto decodificado en formato hexadecimal (para una inspección más fácil)
    print(f"DEBUG: Secreto JWT decodificado (hex): {SUPABASE_JWT_SECRET_DECODED.hex()}")
    print(f"DEBUG: Secreto JWT decodificado (primeros 5 bytes): {SUPABASE_JWT_SECRET_DECODED[:5]}")
except Exception as e:
    print(f"ERROR: Falló la decodificación del secreto JWT de Base64: {e}")
    SUPABASE_JWT_SECRET_DECODED = None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print(f"DEBUG: Token recibido para decodificación: {token}")

    if SUPABASE_JWT_SECRET_DECODED is None:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración del servidor: secreto JWT no disponible."
        )

    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET_DECODED, algorithms=[SUPABASE_JWT_ALGORITHM])
        print(f"DEBUG: Payload decodificado exitosamente: {payload}")
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: el payload no contiene 'sub'."
            )
        return user_id
    except JWTError as e:
        print(f"ERROR: JWTError capturado: {e}") # Muestra el error específico de JWT
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {e}"
        )
    except Exception as e:
        print(f"ERROR: Error inesperado en get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar el token."
        )