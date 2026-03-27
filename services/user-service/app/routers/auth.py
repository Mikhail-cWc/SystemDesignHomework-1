from fastapi import APIRouter, HTTPException

from app.schemas.user import LoginRequest, TokenOut, UserCreate, UserWithToken
from app.services import auth_service, user_service
from app import storage

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=UserWithToken)
def register(data: UserCreate):
    if storage.login_exists(data.login):
        raise HTTPException(status_code=409, detail="Login already taken")
    user = user_service.create_user(data)
    token = auth_service.create_token(user["id"], user["login"])
    return UserWithToken(
        id=user["id"],
        login=user["login"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        access_token=token,
    )


@router.post("/login", status_code=200, response_model=TokenOut)
def login(data: LoginRequest):
    user = user_service.authenticate(data.login, data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_service.create_token(user["id"], user["login"])
    return TokenOut(access_token=token)
