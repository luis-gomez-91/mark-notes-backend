# app/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError, ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError
import os
import base64
import httpx # Necesario para hacer peticiones HTTP (para JWKS de Supabase)
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import logging

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Configura un logger para ver los mensajes de depuración
logger = logging.getLogger("uvicorn.error")

# Instancia de HTTPBearer para extraer el token del encabezado Authorization
security = HTTPBearer()

# --- Configuración de TU JWT Personalizado (para tu backend) ---
# Obtén la clave secreta Base64 directamente de tus variables de entorno.
SUPABASE_JWT_SECRET_BASE64 = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_JWT_ALGORITHM = "HS256" # El algoritmo que tú usarás para firmar tus tokens

# Obtén la referencia del proyecto Supabase para construir URLs dinámicamente
SUPABASE_PROJECT_REF = os.getenv('SUPABASE_PROJECT_REF')
if not SUPABASE_PROJECT_REF:
    logger.error("SUPABASE_PROJECT_REF no está configurado en las variables de entorno. Necesario para construir URLs de Supabase.")
    raise RuntimeError("SUPABASE_PROJECT_REF no configurado.")

# El 'issuer' (emisor) de TU token personalizado puede ser tu propio dominio, o la URL de tu API
YOUR_API_ISSUER = f"https://{SUPABASE_PROJECT_REF}.supabase.co/api" # O tu dominio real
YOUR_API_AUDIENCE = "mark-notes-backend" # Una audiencia específica para tus tokens

SUPABASE_JWT_SECRET_DECODED = None 
try:
    if SUPABASE_JWT_SECRET_BASE64 is None:
        raise ValueError("SUPABASE_JWT_SECRET no configurado.")
    SUPABASE_JWT_SECRET_DECODED = base64.b64decode(SUPABASE_JWT_SECRET_BASE64)
    logger.debug(f"Secreto JWT backend decodificado (longitud): {len(SUPABASE_JWT_SECRET_DECODED)}")
    logger.debug(f"Secreto JWT backend decodificado (primeros 10 bytes hex): {SUPABASE_JWT_SECRET_DECODED[:10].hex()}")
except Exception as e:
    logger.critical(f"Falló la preparación del secreto JWT del backend al iniciar la app: {e}")
    raise RuntimeError("La aplicación no puede iniciarse sin un secreto JWT válido para firmar.")


# --- Configuración para VERIFICAR JWTs de Supabase (usando sus JWKS) ---
SUPABASE_AUTH_URL = f"https://{SUPABASE_PROJECT_REF}.supabase.co/auth/v1"
SUPABASE_JWKS_URL = f"{SUPABASE_AUTH_URL}/.well-known/jwks.json"
# Cachea las JWKS para no hacer una petición en cada verificación
cached_jwks = {} 

async def get_supabase_jwks():
    """Carga y cachea las JSON Web Key Sets (JWKS) de Supabase."""
    global cached_jwks
    if not cached_jwks:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(SUPABASE_JWKS_URL, timeout=5)
                response.raise_for_status() # Lanza HTTPStatusError si la respuesta es un error 4xx/5xx
                cached_jwks = response.json()
                logger.info("JWKS de Supabase cargadas y cacheadas exitosamente.")
            except Exception as e:
                logger.error(f"No se pudieron cargar las JWKS de Supabase desde {SUPABASE_JWKS_URL}: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Error del servidor al cargar las claves de Supabase para verificación.")
    return cached_jwks['keys']

async def verify_supabase_token(supabase_access_token: str):
    """
    Verifica un access_token de Supabase usando sus JWKS.
    Retorna el payload si es válido, de lo contrario lanza HTTPException.
    """
    jwks = await get_supabase_jwks()
    
    # Supabase puede usar diferentes algoritmos para sus access_tokens (RS256 es común)
    supabase_algorithms = ["RS256", "HS256"] 
    # La audiencia de los tokens de Supabase es "authenticated"
    supabase_audience = "authenticated"

    try:
        payload = jwt.decode(
            supabase_access_token,
            key=jwks, # PyJWT puede usar la lista de JWKS para encontrar la clave correcta
            algorithms=supabase_algorithms,
            audience=supabase_audience,
            issuer=SUPABASE_AUTH_URL, # El issuer de Supabase
            options={"require": ["exp", "iat"]} # Requiere que estas claims estén presentes
        )
        logger.debug(f"Access token de Supabase verificado exitosamente.")
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Supabase expirado.")
    except InvalidAudienceError:
        logger.warning(f"Audiencia de token de Supabase inválida. Esperada: '{supabase_audience}'. Token: {supabase_access_token[:20]}...")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Audiencia del token de Supabase inválida.")
    except InvalidIssuerError:
        logger.warning(f"Emisor de token de Supabase inválido. Esperado: '{SUPABASE_AUTH_URL}'. Token: {supabase_access_token[:20]}...")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Emisor del token de Supabase inválido.")
    except PyJWTError as e:
        logger.error(f"Error de verificación del token de Supabase: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token de Supabase inválido: {e}")
    except Exception as e:
        logger.error(f"Error inesperado al verificar token de Supabase: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al procesar el token de Supabase.")


def create_api_token(user_id: str, email: str = None) -> str:
    """
    Crea un token JWT personalizado para tu API, firmado con TU secreto.
    """
    if SUPABASE_JWT_SECRET_DECODED is None:
        raise RuntimeError("Secreto JWT del backend no disponible para firmar tokens.")

    # Puedes ajustar la duración del token según tus necesidades (ej. 1 hora, 1 día)
    expiration = datetime.now(timezone.utc) + timedelta(hours=24) # Válido por 24 horas
    
    payload = {
        "sub": user_id,
        "email": email, # Opcional: Incluir email u otros datos relevantes del usuario
        "iss": YOUR_API_ISSUER, # Emisor de TU API
        "aud": YOUR_API_AUDIENCE, # Audiencia de TU API
        "exp": int(expiration.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    
    # Firma el token con TU secreto
    token = jwt.encode(payload, SUPABASE_JWT_SECRET_DECODED, algorithm=SUPABASE_JWT_ALGORITHM)
    logger.debug(f"Token personalizado de API creado para usuario {user_id}: {token[:20]}...")
    return token


async def get_current_user_from_api_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependencia de FastAPI para verificar los tokens emitidos por TU PROPIA API.
    Retorna el 'sub' (ID de usuario) si el token es válido.
    """
    token = credentials.credentials
    logger.debug(f"Token de API recibido para decodificación (primeros 20 chars): {token[:20]}...")

    if SUPABASE_JWT_SECRET_DECODED is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración del servidor: secreto JWT no disponible."
        )

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET_DECODED, # ¡Aquí verificamos con TU secreto!
            algorithms=[SUPABASE_JWT_ALGORITHM],
            audience=YOUR_API_AUDIENCE, 
            issuer=YOUR_API_ISSUER, 
            options={"require": ["exp", "iat"]}
        )
        
        logger.debug(f"Token de API decodificado exitosamente: {payload}")

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de API inválido: el payload no contiene un ID de usuario ('sub')."
            )
        
        return user_id

    except ExpiredSignatureError:
        logger.warning("Token de API expirado.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de API expirado.")
    except InvalidAudienceError:
        logger.warning(f"Audiencia del token de API inválida. Esperada: '{YOUR_API_AUDIENCE}'")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Audiencia del token de API inválida.")
    except InvalidIssuerError:
        logger.warning(f"Emisor del token de API inválido. Esperado: '{YOUR_API_ISSUER}'")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Emisor del token de API inválido.")
    except PyJWTError as e:
        logger.error(f"Error de verificación del token de API: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token de API inválido. Detalles: {e}")
    except Exception as e:
        logger.error(f"Error inesperado en get_current_user_from_api_token: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor al procesar el token de API.")