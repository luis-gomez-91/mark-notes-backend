from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users import models as fa_models
from .models import User  # Tu modelo SQLAlchemy de usuario
from .database import AsyncSessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession

SECRET = "YOUR_SECRET_KEY"

class User(fa_models.BaseUser):
    pass

class UserCreate(fa_models.BaseUserCreate):
    pass

class UserUpdate(fa_models.BaseUserUpdate):
    pass

class UserDB(User, fa_models.BaseUserDB):
    pass

async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(UserDB, session, User)

jwt_strategy = JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=CookieTransport(cookie_name="auth"),
    get_strategy=lambda: jwt_strategy,
)

fastapi_users = FastAPIUsers(
    get_user_db,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
