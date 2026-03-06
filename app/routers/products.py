from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.routers.deps import get_session
from app.crud.cruds import (
    create_product,
    get_product,
    get_products,
    update_product,
    delete_product
)
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new product."""
    return await create_product(
        session=session,
        title=product_data.title,
        description=product_data.description,
        image=product_data.image,
        sku=product_data.sku,
        price=product_data.price,
        category_id=product_data.category_id
    )


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get a list of products with pagination and category filter."""
    products = await get_products(
        session=session,
        skip=skip,
        limit=limit,
        category_id=category_id
    )
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_endpoint(
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific product by ID."""
    product = await get_product(session=session, product_id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a product."""
    product = await update_product(
        session=session,
        product_id=product_id,
        title=product_data.title,
        description=product_data.description,
        image=product_data.image,
        sku=product_data.sku,
        price=product_data.price,
        category_id=product_data.category_id
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_endpoint(
    product_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a product."""
    success = await delete_product(session=session, product_id=product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )