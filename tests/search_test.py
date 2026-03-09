from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import SearchRequest
from app.services.search_service import search_service


@pytest.fixture
async def category(session):
    cat = Category(name="Search Test Category")
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    yield cat
    await session.delete(cat)
    await session.commit()


@pytest.fixture
async def products(session, category):
    items = [
        Product(title="TESTONLY Red Zorbag", description="A red bag", image="img.jpg",
                sku="SRCH-SKU-001", price=Decimal("25.00"), category_id=category.id),
        Product(title="TESTONLY Blue Zorwallet", description="A blue wallet", image="img.jpg",
                sku="SRCH-SKU-002", price=Decimal("75.00"), category_id=category.id),
        Product(title="TESTONLY Green Zorbag", description="A green bag", image="img.jpg",
                sku="SRCH-BAG-003", price=Decimal("15.00"), category_id=category.id),
    ]
    session.add_all(items)
    await session.commit()
    for p in items:
        await session.refresh(p)
    yield items
    for p in items:
        await session.delete(p)
    await session.commit()


async def test_search_by_name_and_category(session, products, category):
    params = SearchRequest(name="Zorbag", category_id=category.id)
    result = await search_service.search(session, params)

    titles = {p.title for p in result.products}
    assert "TESTONLY Red Zorbag" in titles
    assert "TESTONLY Green Zorbag" in titles
    assert "TESTONLY Blue Zorwallet" not in titles
    assert result.total == 2


async def test_search_by_name_and_price_range(session, products):
    params = SearchRequest(name="Zorbag", min_price=20, max_price=30)
    result = await search_service.search(session, params)

    assert result.total == 1
    assert result.products[0].title == "TESTONLY Red Zorbag"


async def test_search_by_sku_and_category(session, products, category):
    params = SearchRequest(sku="SRCH-SKU", category_id=category.id)
    result = await search_service.search(session, params)

    skus = {p.sku for p in result.products}
    assert "SRCH-SKU-001" in skus
    assert "SRCH-SKU-002" in skus
    assert "SRCH-BAG-003" not in skus
    assert result.total == 2


async def test_search_by_sku_and_price_range(session, products):
    params = SearchRequest(sku="SRCH-BAG", min_price=10, max_price=20)
    result = await search_service.search(session, params)

    assert result.total == 1
    assert result.products[0].sku == "SRCH-BAG-003"


async def test_search_pagination(session, products, category):
    params = SearchRequest(name="Zorbag", category_id=category.id, limit=1, offset=0)
    result = await search_service.search(session, params)

    assert len(result.products) == 1
    assert result.total == 2
    assert result.limit == 1
    assert result.offset == 0


async def test_search_pagination_second_page(session, products, category):
    params = SearchRequest(name="Zorbag", category_id=category.id, limit=1, offset=1)
    result = await search_service.search(session, params)

    assert len(result.products) == 1
    assert result.total == 2


async def test_search_no_results(session, products, category):
    params = SearchRequest(name="Nonexistent XYZ Zorquux", category_id=category.id)
    result = await search_service.search(session, params)

    assert result.total == 0
    assert result.products == []


async def test_search_result_includes_category_name(session, products, category):
    params = SearchRequest(sku="SRCH-SKU-001", category_id=category.id)
    result = await search_service.search(session, params)

    assert result.total == 1
    assert result.products[0].category_name == "Search Test Category"


def test_name_and_sku_mutually_exclusive():
    with pytest.raises(ValidationError, match="mutually exclusive"):
        SearchRequest(name="bag", sku="SKU-001", category_id=1)
