import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.database.session import get_session
from app.services.category_service import CategoryService
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category_endpoint(
    category_data: CategoryCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new category."""
    return await CategoryService.create_category(
        session=session,
        name=category_data.name,
        parent_id=category_data.parent_id
    )


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get a list of categories with pagination and parent filter."""
    categories = await CategoryService.get_categories(
        session=session,
        skip=skip,
        limit=limit,
        parent_id=parent_id
    )
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_endpoint(
    category_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific category by ID."""
    category = await CategoryService.get_category(session=session, category_id=category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category_endpoint(
    category_id: int,
    category_data: CategoryUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a category."""
    try:
        category = await CategoryService.update_category(
            session=session,
            category_id=category_id,
            name=category_data.name,
            parent_id=category_data.parent_id
        )
    except ValueError as exc:
        logger.warning("Category update rejected for id=%s: %s", category_id, exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_endpoint(
    category_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a category."""
    try:
        success = await CategoryService.delete_category(session=session, category_id=category_id)
    except ValueError as exc:
        logger.warning("Category delete rejected for id=%s: %s", category_id, exc)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )