from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., description="Category name", max_length=100)
    parent_id: Optional[int] = Field(None, description="Parent category ID")


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, description="Category name", max_length=100)
    parent_id: Optional[int] = Field(None, description="Parent category ID")


class CategoryChild(BaseModel):
    """Flat child category (no further nesting)."""
    id: int
    name: str
    parent_id: Optional[int]

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    children: List[CategoryChild] = []

    class Config:
        from_attributes = True