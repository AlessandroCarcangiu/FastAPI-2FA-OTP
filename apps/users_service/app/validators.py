import re
from .exceptions import EMAIL_NOT_VALID, PASSWORD_NOT_VALID


pattern_email = r"^\S+@\S+\.\S+$"
pattern_password = r"[A-Za-z0-9@#$%^&+=]{8,}"


def email_validator(email:str) -> bool:
    match = re.fullmatch(pattern_email, email)
    if match:
        return True
    raise EMAIL_NOT_VALID


def password_validator(password:str) -> bool:
    match = re.fullmatch(pattern_password, password)
    if match:
        return True
    raise PASSWORD_NOT_VALID
