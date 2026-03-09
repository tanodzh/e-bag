import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.product import SearchRequest, SearchResponse
from app.services.search_service import search_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=SearchResponse)
async def search_products(
    name: str | None = Query(None, description="Search by product title"),
    sku: str | None = Query(None, description="Search by SKU"),
    min_price: float | None = Query(None, gt=0, description="Minimum price"),
    max_price: float | None = Query(None, gt=0, description="Maximum price"),
    category_id: int | None = Query(None, description="Category ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    try:
        params = SearchRequest(
            name=name, sku=sku, min_price=min_price, max_price=max_price,
            category_id=category_id, limit=limit, offset=offset,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        return await search_service.search(session, params)
    except Exception as e:
        logger.error("Search failed: %s", e)
        raise HTTPException(status_code=500, detail="Search failed")
