from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "trips" ADD "status" VARCHAR(9) NOT NULL  DEFAULT 'planned';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "trips" DROP COLUMN "status";"""
