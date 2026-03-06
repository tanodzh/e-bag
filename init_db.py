"""Initialize MariaDB database schema

Run this script to create database tables for MariaDB.

"""
import logging
import asyncio

from app.database.session import Base, engine

logger = logging.getLogger(__name__)


async def init_db():
    """Create all tables in MariaDB."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("✓ MariaDB tables created successfully")
    logger.info("  - products")
    logger.info("  - categories")


if __name__ == "__main__":
    asyncio.run(init_db())