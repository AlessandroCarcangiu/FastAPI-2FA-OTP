import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from .models import Users
from .routes import auth_app, users_app
from .settings import DB_URL


app = FastAPI(title="User APP")


app.include_router(auth_app, prefix='/api/v1/auth', tags=['auth'])
app.include_router(users_app, prefix='/api/v1/users', tags=['users'])

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
