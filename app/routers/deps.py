from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.database.session import async_session_maker

def get_session() -> AsyncSession:
    """Dependency injection for database sessions."""
    return async_session_maker