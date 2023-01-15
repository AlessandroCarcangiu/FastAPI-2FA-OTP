from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "otps" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "temp_token" VARCHAR(255) NOT NULL,
    "otp" VARCHAR(255) NOT NULL
);;
        ALTER TABLE "users" RENAME COLUMN "safe_login" TO "is_2fa";
        ALTER TABLE "users" ADD "is_active" BOOL NOT NULL  DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" RENAME COLUMN "is_2fa" TO "safe_login";
        ALTER TABLE "users" ADD "safe_login" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users" DROP COLUMN "is_active";
        DROP TABLE IF EXISTS "otps";"""
