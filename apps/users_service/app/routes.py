from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List, Optional
from .exceptions import (
    EMAIL_DUPLICATE,
    PASSWORD_CONFIRM_PASSWORD_NOT_VALID,
    OTP_NOT_VALID,
    NOT_FOUND
)
from .models import User_Pydantic, Users
from .schemas import (
    BaseUpdateUserInput,
    CreateUserInput,
    UpdateUserInput,
    UpdatePasswordInput,
    OTP,
    JWToken,
    TemporaryToken,
    JWTokenUserDescriber,
    Response
)
from .utils import AuthUtils, OTPUtils, UsersUtils, get_current_admin_by_token


auth_app = APIRouter()
users_app = APIRouter()


@auth_app.post(
    "/token",
)
async def token(credentials: OAuth2PasswordRequestForm = Depends()) -> JWToken | TemporaryToken:
    user = await Users.get_or_none(username=credentials.username, is_active=True)
    if user and AuthUtils.check_password(credentials.password, user):
        # if user.is_2fa is false -> generate and return access_token + refresh_token
        # otherwise -> generate and return a temporary token + send a fake email (see otp-logs.txt)
        if not user.is_2fa:
            return JWToken(**AuthUtils.generate_token(JWTokenUserDescriber(**user.__dict__)))
        temporary_token = AuthUtils.generate_temporary_token(user_id=user.id)
        otp = await OTPUtils.generate_otp(temporary_token)
        OTPUtils.log_otp(otp, user.email)
        return TemporaryToken(temporary_token=temporary_token)
    raise HTTPException(status_code=400, detail="Incorrect username or password")


@auth_app.post("/refresh-token")
async def refresh_token(user: User_Pydantic = Depends(UsersUtils.get_user_by_refresh_token)) -> JWToken:
    return JWToken(**AuthUtils.generate_token(JWTokenUserDescriber(**user.__dict__)))


@auth_app.post("/verify-token",)
async def verify_token(user: User_Pydantic = Depends(UsersUtils.get_current_user_by_token)) -> Response:
    return Response(message=bool(user))


@auth_app.post("/verify-otp")
async def verify_otp(body: OTP, data: dict = Depends(UsersUtils.get_current_user_by_temp_token)) -> JWToken:
    if not await OTPUtils.verify_otp(body.otp, data.get("temp_token")):
        raise OTP_NOT_VALID
    return JWToken(**AuthUtils.generate_token(JWTokenUserDescriber(**data.get("user").__dict__)))


@users_app.post("/registration", response_model=User_Pydantic)
async def registration(user_data: CreateUserInput) -> User_Pydantic:
    user_data.password = AuthUtils.encode_password(user_data.password)
    if await Users.get_or_none(email=user_data.email):
       raise EMAIL_DUPLICATE
    user = await Users.create(**user_data.dict())
    return await User_Pydantic.from_tortoise_orm(user)


@users_app.get(
    "/me",
    response_model=User_Pydantic
)
async def me(user: User_Pydantic = Depends(UsersUtils.get_current_user_by_token)) -> User_Pydantic:
    return user


@users_app.get("/", response_model=List[User_Pydantic])
async def users(
        user: User_Pydantic = Depends(get_current_admin_by_token),
        user_id: Optional[int] = None
) -> List[User_Pydantic]:
    return await User_Pydantic.from_queryset(Users.filter(id=user_id) if user_id else Users.all())


@users_app.patch(
    "/",
    response_model=User_Pydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def user_update(
        user_data: UpdateUserInput, user: User_Pydantic = Depends(UsersUtils.get_current_user_by_token),
        user_id: Optional[int] = None
) -> User_Pydantic:
    if not user.is_admin:
        user_data = BaseUpdateUserInput(**user_data.dict(exclude_unset=True))
    user_id = user.id if not user_id else user_id
    await Users.filter(id=user_id).update(**user_data.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@users_app.post(
    "/change-password",
    response_model=Response,
    responses={404: {"model": HTTPNotFoundError}}
)
async def update_password(data: UpdatePasswordInput, user: User_Pydantic = Depends(UsersUtils.get_current_user_by_token)) -> Response:
    if data.password != data.confirm_password:
        raise PASSWORD_CONFIRM_PASSWORD_NOT_VALID
    password = AuthUtils.encode_password(data.password)
    await Users.filter(id=user.id).update(password=password)
    return Response(message="Password updated")


@users_app.delete(
    "/",
    response_model=Response,
    responses={404: {"model": HTTPNotFoundError}}
)
async def user_delete(
        user: User_Pydantic = Depends(UsersUtils.get_current_user_by_token),
        user_id: Optional[int] = None
) -> Response:
    if not user.is_admin or not user_id:
        user_id = user.id
    deleted_count = await Users.filter(id=user_id).delete()
    if not deleted_count:
        raise NOT_FOUND
    return Response(message=f"User with id:'{user_id}' deleted successfully")
