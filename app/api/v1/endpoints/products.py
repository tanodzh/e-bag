import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_session
from app.services.product_service import ProductService
from app.schemas.product import ProductUpdate, ProductResponse

router = APIRouter()

_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    title: str = Form(...),
    sku: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session)
):
    """Create a new product. Send as multipart/form-data; include 'image' field for file upload."""
    image_url: Optional[str] = None

    if image is not None:
        if image.content_type not in _ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported image type '{image.content_type}'. Allowed: {sorted(_ALLOWED_IMAGE_TYPES)}"
            )
        suffix = Path(image.filename).suffix if image.filename else ""
        filename = f"{uuid.uuid4().hex}{suffix}"
        dest = Path(settings.UPLOAD_DIR) / filename
        dest.write_bytes(await image.read())
        image_url = f"{settings.BASE_URL}/media/products/{filename}"

    return await ProductService.create_product(
        session=session,
        title=title,
        description=description,
        image=image_url,
        sku=sku,
        price=price,
        category_id=category_id
    )


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get a list of products with pagination and category filter."""
    products = await ProductService.get_products(
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
    product = await ProductService.get_product(session=session, product_id=product_id)
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
    product = await ProductService.update_product(
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
    success = await ProductService.delete_product(session=session, product_id=product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )