from fastapi import HTTPException, status
from tortoise.exceptions import ValidationError


NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not found"
)

# Data input
EMAIL_NOT_VALID = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email not valid",
)

PASSWORD_NOT_VALID = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Password must be length at least 8 characters",
)

PASSWORD_CONFIRM_PASSWORD_NOT_VALID = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Password and confirm password must be equal",
)

EMAIL_DUPLICATE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User already exists",
)

# Auth
CREDENTIALS_NOT_VALID = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Incorrect username or password",
)

AUTH_SETTINGS_UPDATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication settings are updated, please login again",
)

MULTI_FACTOR_REQUIRED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Multi-factor authentication required",
)

MULTI_FACTOR_NOT_REQUIRED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Multi-factor authentication not required",
)

TOKEN_NOT_VALID = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token not valid",
)

OTP_NOT_VALID = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="OTP not valid",
)

PERMISSION_DENIED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions",
)
