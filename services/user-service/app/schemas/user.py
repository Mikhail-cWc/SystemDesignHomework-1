from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    login: str
    first_name: str
    last_name: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserWithToken(BaseModel):
    id: int
    login: str
    first_name: str
    last_name: str
    access_token: str
    token_type: str = "bearer"
