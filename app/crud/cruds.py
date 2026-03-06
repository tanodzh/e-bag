from typing import Optional, List

from sqlalchemy import select

from app.models.category import Category
from app.models.product import Product


async def create_product(
    session,
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


async def get_product(session, product_id: int) -> Optional[Product]:
    """Get a product by ID."""
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    return result.scalar_one_or_none()


async def get_products(
    session,
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


async def update_product(
    session,
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


async def delete_product(session, product_id: int) -> bool:
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


async def create_category(
    session,
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


async def get_category(session, category_id: int) -> Optional[Category]:
    """Get a category by ID."""
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()


async def get_categories(
    session,
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


async def update_category(
    session,
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


async def delete_category(session, category_id: int) -> bool:
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