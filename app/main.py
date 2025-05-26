from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .auth import fastapi_users, auth_backend
from .database import Base, engine
import asyncio
from authlib.integrations.starlette_client import OAuth

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia por tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"],
)

# Aquí agregarás rutas para notas, directorios, suscripciones, etc.
oauth = OAuth()
oauth.register(
    name='google',
    client_id='TU_CLIENT_ID',
    client_secret='TU_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.get('/auth/google')
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/google/callback')
async def auth_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    # Aquí validas o creas el usuario en la DB y generas tu JWT token.
    return user_info