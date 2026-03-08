from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse


class CategoryService:
    """Service for managing categories."""

    @staticmethod
    async def create_category(
        session: AsyncSession,
        name: str,
        parent_id: Optional[int] = None
    ) -> Category:
        """Create a new category."""
        category = Category(
            name=name,
            parent_id=parent_id
        )
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def get_category(session: AsyncSession, category_id: int) -> Optional[Category]:
        """Get a category by ID."""
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_categories(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[int] = None
    ) -> List[Category]:
        """Get categories with optional parent filter and pagination."""
        query = select(Category)
        
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)
        
        query = query.offset(skip).limit(limit).order_by(Category.created_at.desc())
        
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_category(
        session: AsyncSession,
        category_id: int,
        name: Optional[str] = None,
        parent_id: Optional[int] = None
    ) -> Optional[Category]:
        """Update a category."""
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        
        if category is None:
            return None
        
        if name is not None:
            category.name = name
        if parent_id is not None:
            category.parent_id = parent_id
        
        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def delete_category(session: AsyncSession, category_id: int) -> bool:
        """Delete a category."""
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        
        if category is None:
            return False
        
        await session.delete(category)
        await session.commit()
        return True

    @staticmethod
    async def search_categories(
        session: AsyncSession,
        query_params: str = None,
        parent_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """
        Search categories with filtering capabilities.

        Args:
            session: Async database session
            query_params: Search term for category name
            parent_id: Filter by parent category ID
            skip: Pagination offset
            limit: Number of results to return

        Returns:
            List of matching categories
        """
        query = select(Category)
        
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)
        
        if query_params and query_params.strip():
            search_term = f"%{query_params.strip()}%"
            query = query.where(Category.name.ilike(search_term))
        
        query = query.offset(skip).limit(limit).order_by(Category.created_at.desc())
        
        result = await session.execute(query)
        return list(result.scalars().all())