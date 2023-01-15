import os
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from .validators import email_validator


class Users(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, validators=[email_validator])
    username = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255, null=True)
    lastname = fields.CharField(max_length=255, null=True)
    password = fields.BinaryField()
    is_admin = fields.BooleanField(default=False)
    is_2fa = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    def full_name(self) -> str:
        return f"{self.name} {self.lastname}"

    class PydanticMeta:
        computed = ["full_name"]
        exclude = ["password"]


class OTPs(models.Model):
    id = fields.IntField(pk=True)
    temp_token = fields.CharField(max_length=255)
    otp = fields.CharField(max_length=255)
    active = fields.BooleanField(default=True)

    class PydanticMeta:
        unique_together = ["temp_token", "otp"]


User_Pydantic = pydantic_model_creator(Users, name="User", exclude=('password',))
