from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header

from app.schemas.user import UserOut
from app.services import auth_service, user_service

router = APIRouter(prefix="/users", tags=["users"])


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    payload = auth_service.decode_token(token)
    return {"user_id": int(payload["sub"]), "login": payload["login"]}


@router.get("/by-login", response_model=UserOut)
def get_by_login(login: str, _: dict = Depends(get_current_user)):
    user = user_service.get_by_login(login)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/search", response_model=list[UserOut])
def search(q: str, _: dict = Depends(get_current_user)):
    return user_service.search_by_name(q)
