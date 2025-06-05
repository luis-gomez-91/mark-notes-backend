from .models import Nota
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.routers import protected_routes, notes, create_note, login

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "success", "message": "Bienvenido a la API de Marknotes (ruta pública)."}

app.include_router(notes.router)
app.include_router(protected_routes.router)
app.include_router(create_note.router)
app.include_router(login.router)
