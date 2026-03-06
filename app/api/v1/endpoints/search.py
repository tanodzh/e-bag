from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.routers.deps import get_session
from app.services.search_service import SearchService
from app.schemas.product import SearchRequest, SearchResponse

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_products(
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """
    Search products with flexible filtering.
    
    - `q`: Search term for title or SKU (case-insensitive)
    - `min_price`: Minimum price filter
    - `max_price`: Maximum price filter
    - `category_id`: Filter by category
    - `limit`: Maximum number of results (default: 100, max: 1000)
    - `offset`: Pagination offset
    """
    search_params = SearchRequest(
        q=q,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
        limit=limit,
        offset=offset
    )
    
    return await SearchService.search_products(session, search_params)