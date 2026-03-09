from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator


class ProductCategory(BaseModel):
    """Schema for product category association."""
    id: int
    name: str

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product schema."""
    title: str = Field(..., description="Product title", max_length=200)
    description: Optional[str] = Field(None, description="Product description")
    image: Optional[str] = Field(None, description="Product image URL")
    sku: str = Field(..., description="Unique product SKU", max_length=50)
    price: float = Field(..., description="Product price", gt=0)
    category_id: int = Field(..., description="Category ID")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    image: Optional[str] = Field(None, description="Base64 encoded image with data URI prefix (e.g. data:image/png;base64,...)")


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    title: Optional[str] = Field(None, description="Product title", max_length=200)
    description: Optional[str] = Field(None, description="Product description")
    image: Optional[str] = Field(None, description="Product image URL")
    sku: Optional[str] = Field(None, description="Unique product SKU", max_length=50)
    price: Optional[float] = Field(None, description="Product price", gt=0)
    category_id: Optional[int] = Field(None, description="Category ID")


class ProductResponse(BaseModel):
    """Schema for product response."""
    id: int
    title: str
    description: Optional[str]
    image: Optional[str]
    sku: str
    price: float
    category_id: int
    category: Optional[ProductCategory]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductSearchResult(BaseModel):
    """Schema for search result."""
    id: int
    title: str
    description: Optional[str]
    image: Optional[str]
    sku: str
    price: float
    category_id: int
    category_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Schema for search request parameters."""
    name: Optional[str] = Field(None, description="Search by product title (ilike)")
    sku: Optional[str] = Field(None, description="Search by SKU (ilike)")
    min_price: Optional[float] = Field(None, description="Minimum price filter", gt=0)
    max_price: Optional[float] = Field(None, description="Maximum price filter", gt=0)
    category_id: Optional[int] = Field(None, description="Category filter")
    limit: int = Field(100, ge=1, le=1000, description="Max results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")

    @model_validator(mode="after")
    def validate_combinations(self) -> "SearchRequest":
        if self.name and self.sku:
            raise ValueError("name and sku are mutually exclusive")
        return self


class SearchResponse(BaseModel):
    """Schema for search response."""
    products: List[ProductSearchResult]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True