import asyncio
from tortoise import Tortoise
from . import models
from . import settings
from . import utils


async def init():
    await Tortoise.init(
        db_url=settings.DB_URL,
        modules={'models': ['app.models']}
    )
    await Tortoise.generate_schemas()
    users = [
        {
            "id": 1,
            "email": "rs.smith@test.com",
            "username": "rs.smith@test.com",
            "name": "Robert",
            "lastname": "Smith",
            "password": 'testtest11&@admin',
            "is_2fa": True,
            "is_admin": True
        },
        {
            "id": 2,
            "email": "dv.gahan@test.com",
            "username": "dv.gahan@test.com",
            "name": "Dave",
            "lastname": "Gahan",
            "password": 'testtest11&@',
        },
    ]
    for user in users:
        try:
            await models.Users.filter(id=user.get("id")).delete()
            user["password"] = utils.AuthUtils.encode_password(user["password"])
            await models.Users(**user).save()
        except:
            pass
    await Tortoise.close_connections()


asyncio.run(init())

# models.Users(
#     id=1,
#     email="rs.smith@test.com",
#     username="rs.smith@test.com",
#     name="Robert",
#     lastname="Smith",
#     password=b'\x24326224313224524a6945786a366b66732e704c2f7547792f6a3968756838466b4861544c2e4e374b784f302e3338686c46575963674859596b726d',
#     is_2fa=True,
#     is_admin=True
# ),
# models.Users(
#     id=2,
#     email="dv.gahan@test.com",
#     username="dv.gahan@test.com",
#     name="Dave",
#     lastname="Gahan",
#     password=b'\x243262243132246239426449776d504c6e53446365516b6e675542344f544c2f74746f4168324f366c3431726237434c386f4e63394d67332e6b792e',
# )
