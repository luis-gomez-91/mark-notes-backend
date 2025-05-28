from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.routers import protected_routes, notes
from .models import Nota

app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Hola Mundo"}

app.include_router(notes.router)
app.include_router(protected_routes.router)