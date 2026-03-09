import base64
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_session
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

logger = logging.getLogger(__name__)
router = APIRouter()

_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_MEDIA_PREFIX = "/media/products/"
_EXT_MAP = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}


def _image_url_to_path(image_url: str) -> Optional[Path]:
    """Resolve a stored image URL back to its path on disk, or None if not a local upload."""
    idx = image_url.find(_MEDIA_PREFIX)
    if idx == -1:
        return None
    return Path(settings.UPLOAD_DIR) / image_url[idx + len(_MEDIA_PREFIX):]


def _save_base64_image(data: str) -> tuple[Path, str]:
    """Decode a base64 data URI, save to disk, return (dest_path, image_url)."""
    if not data.startswith("data:"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid image data")
    try:
        header, encoded = data.split(",", 1)
        mime = header.split(":")[1].split(";")[0]
    except (ValueError, IndexError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid image data")
    if mime not in _ALLOWED_IMAGE_TYPES:
        logger.warning("Rejected unsupported image MIME type: %s", mime)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid image data")
    try:
        image_bytes = base64.b64decode(encoded)
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid image data")
    filename = f"{uuid.uuid4().hex}{_EXT_MAP[mime]}"
    dest = Path(settings.UPLOAD_DIR) / filename
    dest.write_bytes(image_bytes)
    return dest, f"{settings.BASE_URL}/media/products/{filename}"


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new product. The 'image' field accepts a base64 data URI (data:image/png;base64,...)."""
    logger.debug("Creating product: sku=%s title=%r category_id=%s price=%s",
                 product_data.sku, product_data.title, product_data.category_id, product_data.price)

    image_url: Optional[str] = None
    dest: Optional[Path] = None

    if product_data.image is not None:
        dest, image_url = _save_base64_image(product_data.image)
        logger.debug("Image saved: url=%s", image_url)

    try:
        product = await ProductService.create_product(
            session=session,
            title=product_data.title,
            description=product_data.description,
            image=image_url,
            sku=product_data.sku,
            price=product_data.price,
            category_id=product_data.category_id
        )
        logger.debug("Product created: id=%s sku=%s", product.id, product.sku)
        return product
    except Exception as exc:
        if dest is not None:
            dest.unlink(missing_ok=True)
            logger.debug("Cleaned up orphaned image: %s", dest)
        logger.error("Failed to create product sku=%r: %s", product_data.sku, str(exc).splitlines()[0])
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create product")


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
    try:
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
    except Exception as exc:
        logger.error("Failed to update product id=%s: %s", product_id, str(exc).splitlines()[0])
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update product")
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
    """Delete a product and its associated image file."""
    logger.debug("Deleting product: id=%s", product_id)
    product = await ProductService.get_product(session=session, product_id=product_id)
    if product is None:
        logger.debug("Product not found: id=%s", product_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    image_path = _image_url_to_path(product.image) if product.image else None

    await ProductService.delete_product(session=session, product_id=product_id)
    logger.debug("Product deleted from DB: id=%s sku=%s", product_id, product.sku)

    if image_path is not None:
        image_path.unlink(missing_ok=True)
        logger.debug("Deleted image file: %s", image_path)