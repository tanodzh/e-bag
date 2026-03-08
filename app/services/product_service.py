from typing import Optional, List

from sqlalchemy import select, func, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductSearchResult


class ProductService:
    """Service for managing products."""

    @staticmethod
    async def create_product(
        session: AsyncSession,
        title: str,
        description: Optional[str] = None,
        image: Optional[str] = None,
        sku: Optional[str] = None,
        price: Optional[float] = None,
        category_id: Optional[int] = None
    ):
        """Create a new product."""
        product = Product(
            title=title,
            description=description,
            image=image,
            sku=sku,
            price=price,
            category_id=category_id
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product

    @staticmethod
    async def get_product(session: AsyncSession, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_products(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None
    ) -> List[Product]:
        """Get products with optional category filter and pagination."""
        query = select(Product)
        
        if category_id:
            query = query.where(Product.category_id == category_id)
        
        query = query.offset(skip).limit(limit).order_by(Product.created_at.desc())
        
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_product(
        session: AsyncSession,
        product_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        image: Optional[str] = None,
        sku: Optional[str] = None,
        price: Optional[float] = None,
        category_id: Optional[int] = None
    ) -> Optional[Product]:
        """Update a product."""
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if product is None:
            return None
        
        if title is not None:
            product.title = title
        if description is not None:
            product.description = description
        if image is not None:
            product.image = image
        if sku is not None:
            product.sku = sku
        if price is not None:
            product.price = price
        if category_id is not None:
            product.category_id = category_id
        
        await session.commit()
        await session.refresh(product)
        return product

    @staticmethod
    async def delete_product(session: AsyncSession, product_id: int) -> bool:
        """Delete a product."""
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if product is None:
            return False
        
        await session.delete(product)
        await session.commit()
        return True
