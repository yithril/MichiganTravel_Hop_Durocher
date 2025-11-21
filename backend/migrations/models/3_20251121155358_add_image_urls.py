from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "attractions" ADD "image_url" VARCHAR(500);
        ALTER TABLE "trips" ADD "cover_image_url" VARCHAR(500);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "trips" DROP COLUMN "cover_image_url";
        ALTER TABLE "attractions" DROP COLUMN "image_url";"""
