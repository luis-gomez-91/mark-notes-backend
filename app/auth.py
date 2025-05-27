from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
import requests

SUPABASE_PROJECT_ID = "wfojlrhaxxgxcfoimhgj"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
AUDIENCE = SUPABASE_PROJECT_ID  # El mismo que tu "ref"
ISSUER = f"{SUPABASE_URL}/auth/v1"

security = HTTPBearer()
jwks = requests.get(JWKS_URL).json()  # Idealmente cachear en producción

def verify_token(token: str):
    try:
        unverified_header = jwt.get_unverified_header(token)
        key = next(k for k in jwks["keys"] if k["kid"] == unverified_header["kid"])
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER
        )
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token=Depends(security)):
    return verify_token(token.credentials)
