import bcrypt
import datetime
import jwt
import pyotp
from fastapi import Depends
from tortoise.contrib.fastapi import HTTPNotFoundError
from .exceptions import (
    MULTI_FACTOR_NOT_REQUIRED,
    TOKEN_NOT_VALID,
    PERMISSION_DENIED
)
from .models import OTPs, Users, User_Pydantic
from .settings import (
    TOKEN_SECRET_KEY,
    TEMPORARY_TOKEN_SECRET_KEY,
    ACCESS_TOKEN_EXPIRE,
    REFRESH_TOKEN_EXPIRE,
    TEMPORARY_TOKEN_EXPIRE,
    JWT_ALGORITHM,
    LOG_FILE
)
from .schemas import (
    oauth2_schema,
    JWTokenUserDescriber,
    Refresh
)
from .validators import password_validator


class OTPUtils:

    @staticmethod
    async def generate_otp(temporary_token:str) -> str:
        secret_key = pyotp.random_base32()
        otp = pyotp.TOTP(secret_key).now()
        await OTPs.create(temp_token=temporary_token, otp=otp)
        return otp

    @staticmethod
    async def verify_otp(otp:str, temp_token: str) -> bool:
        record = await OTPs.get_or_none(otp=otp, temp_token=temp_token, active=True)
        if record:
            await record.update_from_dict({"active":False}).save()
        return bool(record)

    @staticmethod
    def log_otp(otp:str, email:str) -> None:
        with open(LOG_FILE, "w") as f:
            f.write(f"{email}/{otp}")


class AuthUtils:

    @classmethod
    def generate_token(cls, user: JWTokenUserDescriber) -> dict:
        access_token = cls.__generate_token(user.__dict__, TOKEN_SECRET_KEY, ACCESS_TOKEN_EXPIRE)
        refresh_token = cls.refresh_token(user.id, access_token)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    @classmethod
    def generate_temporary_token(cls, user_id: str) -> str:
        return cls.__generate_token({"id": user_id}, TEMPORARY_TOKEN_SECRET_KEY, TEMPORARY_TOKEN_EXPIRE)

    @classmethod
    def refresh_token(cls, id:int, access_token:str) -> str:
        data = {
            "id":id,
            "access_token": access_token
        }
        return cls.__generate_token(data, TOKEN_SECRET_KEY, REFRESH_TOKEN_EXPIRE)

    @staticmethod
    def __generate_token(data:dict, secret_key:str, timedelta:int) -> str:
        data = {
            "exp": datetime.datetime.now()+datetime.timedelta(seconds=timedelta),
            **data
        }
        return jwt.encode(
            data,
            secret_key,
            algorithm = JWT_ALGORITHM
        )

    @classmethod
    def decode_token(cls, token: str = Depends(oauth2_schema)) -> dict:
        return cls.__decode_token(token, TOKEN_SECRET_KEY)

    @classmethod
    def decode_temp_token(cls, token: str = Depends(oauth2_schema)) -> tuple:
        return cls.__decode_token(token, TEMPORARY_TOKEN_SECRET_KEY), token

    @classmethod
    def decode_refresh_token(cls, body: Refresh) -> dict:
        return cls.__decode_token(body.refresh_token, TOKEN_SECRET_KEY)

    @staticmethod
    def __decode_token(token: str, secret_key: str) -> dict:
        try:
            return jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
        except:
            raise TOKEN_NOT_VALID

    @classmethod
    def encode_password(cls, password:str) -> bytes:
        password_validator(password)
        byte_password = password.encode("utf-8")
        my_salt = bcrypt.gensalt()
        return bcrypt.hashpw(byte_password, my_salt)

    @staticmethod
    def check_password(password:str, user:User_Pydantic) -> bool:
        password = password.encode("utf-8")
        return bcrypt.checkpw(password, user.password)


class UsersUtils:

    @classmethod
    async def get_current_user_by_token(cls, decoded_token: dict = Depends(AuthUtils.decode_token)) -> User_Pydantic:
        if "id" in decoded_token:
           return await cls.get_user_by_id(decoded_token.get("id"))
        raise TOKEN_NOT_VALID

    @classmethod
    async def get_current_user_by_temp_token(cls, decoded_token: tuple = Depends(AuthUtils.decode_temp_token)) -> dict:
        if "id" in decoded_token[0]:
            user = await cls.get_user_by_id(decoded_token[0].get("id"))
            if user.is_2fa:
                return {
                    "temp_token": decoded_token[1],
                    "user": user
                }
            raise MULTI_FACTOR_NOT_REQUIRED
        raise TOKEN_NOT_VALID

    @classmethod
    async def get_user_by_refresh_token(cls, decoded_token: dict = Depends(AuthUtils.decode_refresh_token)) -> dict:
        return await cls.get_current_user_by_token(decoded_token=decoded_token)

    @staticmethod
    async def get_user_by_id(user_id: str | int) -> User_Pydantic:
        user = await Users.get_or_none(id=user_id, is_active=True)
        if user:
            return await User_Pydantic.from_tortoise_orm(user)
        raise HTTPNotFoundError


async def get_current_admin_by_token(user: User_Pydantic = Depends(UsersUtils.get_current_user_by_token)) -> User_Pydantic:
    if user.is_admin:
        return user
    raise PERMISSION_DENIED
