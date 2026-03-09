import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_maker


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with async_session_maker() as s:
        yield s
