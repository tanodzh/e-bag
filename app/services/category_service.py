from typing import Optional, List

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product


def _category_query():
    return select(Category).options(selectinload(Category.children))


async def _check_cycle(session: AsyncSession, category_id: int, new_parent_id: int) -> None:
    """Raise ValueError if setting new_parent_id as parent of category_id would create a cycle."""
    current_id = new_parent_id
    while current_id is not None:
        if current_id == category_id:
            raise ValueError(f"Setting parent_id={new_parent_id} would create a cyclic dependency")
        result = await session.execute(
            select(Category.parent_id).where(Category.id == current_id)
        )
        current_id = result.scalar_one_or_none()


class CategoryService:
    """Service for managing categories."""

    @staticmethod
    async def create_category(
        session: AsyncSession,
        name: str,
        parent_id: Optional[int] = None
    ) -> Category:
        """Create a new category."""
        category = Category(name=name, parent_id=parent_id)
        session.add(category)
        await session.commit()
        result = await session.execute(
            _category_query().where(Category.id == category.id)
        )
        return result.scalar_one()

    @staticmethod
    async def get_category(session: AsyncSession, category_id: int) -> Optional[Category]:
        """Get a category by ID."""
        result = await session.execute(
            _category_query().where(Category.id == category_id)
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
        query = _category_query()

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
            await _check_cycle(session, category_id, parent_id)
            category.parent_id = parent_id

        await session.commit()
        result = await session.execute(
            _category_query().where(Category.id == category_id)
        )
        return result.scalar_one()

    @staticmethod
    async def delete_category(session: AsyncSession, category_id: int) -> bool:
        """Delete a category. Raises ValueError if it has children."""
        exists = await session.scalar(select(Category.id).where(Category.id == category_id))
        if exists is None:
            return False

        child_id = await session.scalar(
            select(Category.id).where(Category.parent_id == category_id).limit(1)
        )
        if child_id is not None:
            raise ValueError(f"Cannot delete category {category_id}: it has subcategories")

        product_id = await session.scalar(
            select(Product.id).where(Product.category_id == category_id).limit(1)
        )
        if product_id is not None:
            raise ValueError(f"Cannot delete category {category_id}: it has products")

        await session.execute(delete(Category).where(Category.id == category_id))
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
        """Search categories with filtering capabilities."""
        query = _category_query()

        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)

        if query_params and query_params.strip():
            search_term = f"%{query_params.strip()}%"
            query = query.where(Category.name.ilike(search_term))

        query = query.offset(skip).limit(limit).order_by(Category.created_at.desc())

        result = await session.execute(query)
        return list(result.scalars().all())
