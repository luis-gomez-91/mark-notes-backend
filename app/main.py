from fastapi import FastAPI
from app.routers import protected_routes

app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Hola Mundo"}

app.include_router(protected_routes.router)