from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional


# Web
class Response(BaseModel):
    message: object


# User
class CreateUserInput(BaseModel):
    email: str
    username: str
    name: str
    lastname: str
    password: str
    is_2fa: bool


class BaseUpdateUserInput(BaseModel):
    email: Optional[str]
    username: Optional[str]
    name: Optional[str]
    lastname: Optional[str]
    is_2fa: Optional[bool]


class UpdateUserInput(BaseUpdateUserInput):
    is_staff: Optional[bool]


class UpdatePasswordInput(BaseModel):
    password: str
    confirm_password: str


# JWT
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


class Refresh(BaseModel):
    refresh_token: str


class OTP(BaseModel):
    otp: str


class BaseToken(BaseModel):
    token_type: str = "bearer"


class JWToken(BaseToken):
    access_token: str
    refresh_token: str


class TemporaryToken(BaseToken):
    temporary_token: str


class JWTokenUserDescriber(BaseModel):
    id: int
    email: str
    is_2fa: bool
