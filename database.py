"""Initialize database with migration

Run this script once to create the database schema with all migrations applied.

"""
import logging
import asyncio
from alembic import command

from app.database.session import engine
from alembic.config import Config

logger = logging.getLogger(__name__)

async def init_db():
    """Apply all migrations and create tables."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.connect()))

    command.upgrade(alembic_cfg, "head")

    logger.info("✓ Database schema initialized and migrations applied")


if __name__ == "__main__":
    asyncio.run(init_db())