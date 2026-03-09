import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.schemas.product import SearchRequest, SearchResponse, ProductSearchResult

logger = logging.getLogger(__name__)


class SearchService:
    async def search(self, session: AsyncSession, params: SearchRequest) -> SearchResponse:
        query = select(Product).options(selectinload(Product.category))

        if params.name:
            query = query.where(Product.title.ilike(f"%{params.name}%"))
        if params.sku:
            query = query.where(Product.sku.ilike(f"%{params.sku}%"))
        if params.min_price is not None:
            query = query.where(Product.price >= params.min_price)
        if params.max_price is not None:
            query = query.where(Product.price <= params.max_price)
        if params.category_id is not None:
            query = query.where(Product.category_id == params.category_id)

        count_result = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        result = await session.execute(
            query.order_by(Product.created_at.desc())
                 .limit(params.limit)
                 .offset(params.offset)
        )
        products = result.scalars().all()

        return SearchResponse(
            products=[
                ProductSearchResult(
                    id=p.id,
                    title=p.title,
                    description=p.description,
                    image=p.image,
                    sku=p.sku,
                    price=p.price,
                    category_id=p.category_id,
                    category_name=p.category.name if p.category else None,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
                for p in products
            ],
            total=total,
            limit=params.limit,
            offset=params.offset,
        )


search_service = SearchService()
