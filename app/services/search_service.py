from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductSearchResult, SearchRequest, SearchResponse


class SearchService:
    """Service for product search with filtering capabilities."""

    @staticmethod
    async def search_products(
        session: AsyncSession,
        query_params: SearchRequest
    ) -> SearchResponse:
        """
        Search products with flexible filtering.

        Args:
            session: Async database session
            query_params: Search request parameters

        Returns:
            Search response with paginated results and metadata
        """
        base_query = select(Product).join(Category)

        has_search_term = False
        search_term = None
        min_price = query_params.min_price
        max_price = query_params.max_price
        category_filter = query_params.category_id

        if query_params.q and query_params.q.strip():
            search_term = f"%{query_params.q.strip()}%"
            base_query = base_query.where(
                or_(
                    Product.title.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )
            has_search_term = True

        if min_price is not None:
            base_query = base_query.where(Product.price >= min_price)

        if max_price is not None:
            base_query = base_query.where(Product.price <= max_price)

        if category_filter is not None:
            base_query = base_query.where(Product.category_id == category_filter)

        count_query = select(func.count()).select_from(Product.join(Category))

        if has_search_term:
            count_query = count_query.where(
                or_(
                    Product.title.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )

        if min_price is not None:
            count_query = count_query.where(Product.price >= min_price)

        if max_price is not None:
            count_query = count_query.where(Product.price <= max_price)

        if category_filter is not None:
            count_query = count_query.where(Product.category_id == category_filter)

        total_result = await session.execute(count_query)
        total = total_result.scalar()

        final_query = base_query.offset(query_params.offset).order_by(desc(Product.updated_at))
        final_query = final_query.limit(query_params.limit)

        result = await session.execute(final_query)
        products = result.scalars().all()

        search_results = [
            ProductSearchResult(
                id=product.id,
                title=product.title,
                description=product.description,
                image=product.image,
                sku=product.sku,
                price=product.price,
                category_id=product.category_id,
                category_name=product.category.name if product.category else None,
                created_at=product.created_at,
                updated_at=product.updated_at
            )
            for product in products
        ]

        return SearchResponse(
            products=search_results,
            total=total if total is not None else 0,
            limit=query_params.limit,
            offset=query_params.offset
        )

    @staticmethod
    async def advanced_search(
        session: AsyncSession,
        search_term: None = None,
        min_price: None = None,
        max_price: None = None,
        category_id: None = None,
        skip: None = 0,
        limit: None = 100
    ) -> List[ProductSearchResult]:
        """
        Advanced search with custom parameters.

        Args:
            session: Async database session
            search_term: Search term for title or SKU
            min_price: Minimum price filter
            max_price: Maximum price filter
            category_id: Category filter
            skip: Pagination offset
            limit: Number of results to return

        Returns:
            List of search results
        """
        search_params = SearchRequest(
            q=search_term,
            min_price=min_price,
            max_price=max_price,
            category_id=category_id,
            limit=limit,
            offset=skip
        )

        search_response = await SearchService.search_products(session, search_params)
        return search_response.products