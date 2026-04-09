import asyncpg
from fastapi import APIRouter, HTTPException

from app.schemas.user import LoginRequest, TokenOut, UserCreate, UserWithToken
from app.services import auth_service, user_service
from app import repository
from app.db import get_pool

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=UserWithToken)
async def register(data: UserCreate):
    pool: asyncpg.Pool = get_pool()
    if await repository.login_exists(pool, data.login):
        raise HTTPException(status_code=409, detail="Login already taken")
    user = await user_service.create_user(pool, data)
    token = auth_service.create_token(user["id"], user["login"])
    return UserWithToken(
        id=user["id"],
        login=user["login"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        access_token=token,
    )


@router.post("/login", status_code=200, response_model=TokenOut)
async def login(data: LoginRequest):
    pool: asyncpg.Pool = get_pool()
    user = await user_service.authenticate(pool, data.login, data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_service.create_token(user["id"], user["login"])
    return TokenOut(access_token=token)
