import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import SearchRequest
from app.services.search_service import SearchService


@pytest.fixture
def sample_categories():
    """Create sample categories for testing."""
    categories = [
        Category(name="Electronics", parent_id=None),
        Category(name="Computers", parent_id=1),
        Category(name="Phones", parent_id=1),
        Category(name="Clothing", parent_id=None),
    ]
    return categories


@pytest.fixture
def sample_products():
    """Create sample products for testing."""
    products = [
        Product(
            title="Laptop",
            description="High-performance laptop",
            sku="LAP-001",
            price=999.99,
            category_id=1
        ),
        Product(
            title="Smartphone",
            description="Latest smartphone model",
            sku="PHN-002",
            price=699.99,
            category_id=1
        ),
        Product(
            title="Desktop",
            description="Gaming desktop PC",
            sku="DTK-003",
            price=1299.99,
            category_id=1
        ),
        Product(
            title="T-Shirt",
            description="Cotton T-shirt",
            sku="TSH-001",
            price=19.99,
            category_id=3
        ),
        Product(
            title="Jeans",
            description="Denim jeans",
            sku="JNS-001",
            price=59.99,
            category_id=3
        ),
        Product(
            title="Tablet",
            description="Portable tablet",
            sku="TBL-004",
            price=499.99,
            category_id=1
        ),
    ]
    return products


@pytest.mark.asyncio
async def test_search_with_no_filters(session: AsyncSession, sample_categories, sample_products):
    """Test search with no filters returns all products."""
    for category in sample_categories:
        session.add(category)
    for product in sample_products:
        product.category = sample_categories[product.category_id - 1]
        session.add(product)

    await session.commit()

    search_params = SearchRequest(
        q=None,
        min_price=None,
        max_price=None,
        category_id=None,
        limit=10,
        offset=0
    )

    result = await SearchService.search_products(session, search_params)

    assert result.total == len(sample_products)
    assert len(result.products) == len(sample_products)


@pytest.mark.asyncio
async def test_search_with_text_filter(session: AsyncSession, sample_categories, sample_products):
    """Test search with text filter returns matching products."""
    for category in sample_categories:
        session.add(category)
    for product in sample_products:
        product.category = sample_categories[product.category_id - 1]
        session.add(product)

    await session.commit()

    search_params = SearchRequest(
        q="Phone",
        min_price=None,
        max_price=None,
        category_id=None,
        limit=10,
        offset=0
    )

    result = await SearchService.search_products(session, search_params)

    assert result.total == 2
    assert len(result.products) == 2
    assert result.products[0].title == "Tablet"
    assert result.products[1].title == "Smartphone"


@pytest.mark.asyncio
async def test_search_with_price_range(session: AsyncSession, sample_categories, sample_products):
    """Test search with price range filter."""
    for category in sample_categories:
        session.add(category)
    for product in sample_products:
        product.category = sample_categories[product.category_id - 1]
        session.add(product)

    await session.commit()

    search_params = SearchRequest(
        q=None,
        min_price=500.00,
        max_price=800.00,
        category_id=None,
        limit=10,
        offset=0
    )

    result = await SearchService.search_products(session, search_params)

    assert result.total == 2
    assert len(result.products) == 2
    prices = [p.price for p in result.products]
    assert all(500 <= price <= 800 for price in prices)


@pytest.mark.asyncio
async def test_search_with_category_filter(session: AsyncSession, sample_categories, sample_products):
    """Test search with category filter."""
    for category in sample_categories:
        session.add(category)
    for product in sample_products:
        product.category = sample_categories[product.category_id - 1]
        session.add(product)

    await session.commit()

    search_params = SearchRequest(
        q=None,
        min_price=None,
        max_price=None,
        category_id=1,
        limit=10,
        offset=0
    )

    result = await SearchService.search_products(session, search_params)

    assert result.total == 4
    assert len(result.products) == 4
    assert all(p.category_id == 1 for p in result.products)


@pytest.mark.asyncio
async def test_search_with_combined_filters(session: AsyncSession, sample_categories, sample_products):
    """Test search with combined filters."""
    for category in sample_categories:
        session.add(category)
    for product in sample_products:
        product.category = sample_categories[product.category_id - 1]
        session.add(product)

    await session.commit()

    search_params = SearchRequest(
        q="Tablet",
        min_price=400.00,
        max_price=700.00,
        category_id=1,
        limit=10,
        offset=0
    )

    result = await SearchService.search_products(session, search_params)

    assert result.total == 1
    assert len(result.products) == 1
    assert result.products[0].title == "Tablet"
    assert result.products[0].price == 499.99


@pytest.mark.asyncio
async def test_search_pagination(session: AsyncSession, sample_categories, sample_products):
    """Test search with pagination."""
    for category in sample_categories:
        session.add(category)
    for product in sample_products:
        product.category = sample_categories[product.category_id - 1]
        session.add(product)

    await session.commit()

    search_params = SearchRequest(
        q=None,
        min_price=None,
        max_price=None,
        category_id=None,
        limit=2,
        offset=2
    )

    result = await SearchService.search_products(session, search_params)

    assert result.total == len(sample_products)
    assert len(result.products) == 2
    assert result.offset == 2
    assert result.limit == 2


@pytest.mark.asyncio
async def test_advanced_search(session: AsyncSession, sample_categories, sample_products):
    """Test advanced search method."""
    for category in sample_categories:
        session.add(category)
    for product in sample_products:
        product.category = sample_categories[product.category_id - 1]
        session.add(product)

    await session.commit()

    results = await SearchService.advanced_search(
        session=session,
        search_term="Clothing",
        min_price=10.00,
        max_price=100.00,
        category_id=3,
        skip=0,
        limit=10
    )

    assert len(results) == 2
    titles = {r.title for r in results}
    assert titles == {"T-Shirt", "Jeans"}


@pytest.mark.asyncio
async def test_search_case_insensitive(session: AsyncSession, sample_categories, sample_products):
    """Test search is case-insensitive."""
    for category in sample_categories:
        session.add(category)
    for product in sample_products:
        product.category = sample_categories[product.category_id - 1]
        session.add(product)

    await session.commit()

    search_params = SearchRequest(
        q="PHONE",
        min_price=None,
        max_price=None,
        category_id=None,
        limit=10,
        offset=0
    )

    result = await SearchService.search_products(session, search_params)

    assert result.total == 2
    assert len(result.products) == 2