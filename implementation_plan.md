# E-commerce Service Implementation Plan

## Technology Stack
- **Framework**: FastAPI (modern, async support)
- **Database**: SQLite with Docker for production
- **ORM**: SQLAlchemy 2.0 (async compatible)
- **Validation**: Pydantic v2
- **Testing**: pytest with pytest-asyncio
- **API Documentation**: Swagger UI (built-in)

## Project Structure
```
e-bag/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Configuration settings
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py          # Async database session setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py          # SQLAlchemy Product model
│   │   └── category.py         # SQLAlchemy Category model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── product.py          # Pydantic product schemas
│   │   └── category.py         # Pydantic category schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   └── cruds.py            # CRUD operations (reusable functions)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── products.py  # Product endpoints
│   │   │   │   └── categories.py # Category endpoints
│   │   │   └── router.py       # API v1 router
│   │   └── deps.py            # Dependency injection helpers
│   └── services/
│       ├── __init__.py
│       └── search_service.py  # Search business logic with filters
├── tests/
│   ├── __init__.py
│   └── test_search.py          # Search functionality tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml         # Container orchestration
├── alembic.ini                # Database migration tool (optional)
└── README.md                   # Project documentation

## Core Features

### 1. Database Models

**Category Model:**
- id (integer, PK)
- name (string)
- parent_id (integer, FK nullable)
- created_at/updated_at timestamps
- self-referencing relationship

**Product Model:**
- id (integer, PK)
- title (string)
- description (text)
- image (string - URL)
- sku (string, unique)
- price (decimal)
- category_id (integer, FK)
- created_at/updated_at timestamps
- Relationships to Category, Products

### 2. CRUD Operations

**Product CRUD:**
- create_product(product_data)
- get_product(product_id)
- get_products(filters=None)
- update_product(product_id, product_data)
- delete_product(product_id)

**Category CRUD:**
- create_category(category_data)
- get_category(category_id)
- get_categories(filters=None)
- update_category(category_id, category_data)
- delete_category(category_id)

### 3. Search Endpoint

**API:**
```
GET /api/v1/products/search
Query Parameters:
  - q (optional): Search string for title/SKU
  - min_price (optional): Minimum price filter
  - max_price (optional): Maximum price filter
  - category_id (optional): Category filter
  - limit (optional): Result limit (default: 100)
  - offset (optional): Pagination offset
```

**Features:**
- Full-text search across title and SKU
- Price range filtering
- Category filtering
- Pagination support
- Return formatted results with metadata

### 4. Unit Tests

**Search Tests:**
- Test search by name
- Test search by SKU
- Test combined price range filter
- Test category filtering
- Test edge cases (no results, query not found)
- Test pagination behavior

### 5. API Documentation

**Swagger UI:**
- Auto-generated documentation at `/docs`
- Interactive request examples
- Request/response schemas
- Authentication info display

## Implementation Order

1. **Infrastructure Setup**
   - Initialize FastAPI app
   - Configure environment settings
   - Setup database connections

2. **Database Layer**
   - Create models with relationships
   - Implement CRUD functions
   - Build Pydantic schemas

3. **API Endpoints**
   - Product CRUD endpoints
   - Category CRUD endpoints
   - Search endpoint with filters

4. **Business Logic**
   - Implement search service
   - Add validation logic
   - Error handling

5. **Testing**
   - Write search tests
   - Verify functionality

6. **Deployment Setup**
   - Docker configuration
   - Production considerations

## Production Considerations

- **Async/Await**: Performance optimization for concurrent requests
- **Validation**: Input sanitization and type checking
- **Error Handling**: Proper HTTP status codes and error messages
- **Migration Support**: Database version control (Alembic)
- **Swagger UI**: For development and documentation
- **Environment Variables**: Secure configuration management

## Dependencies
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0
- sqlalchemy>=2.0.0
- pydantic>=2.0.0
- pydantic-settings>=2.0.0
- asyncio
- pytest>=7.4.0
- pytest-asyncio>=0.21.0
- alembic>=1.12.0
```

## Key Design Decisions

1. **Async Architecture**: Modern and efficient, handles high concurrency
2. **Separation of Concerns**: Models, schemas, CRUD, and services are isolated
3. **Reusability**: CRUD functions can be reused in endpoints and tests
4. **Extensibility**: Easy to add filters and operations later
5. **Testability**: Clear separation allows focused unit testing
6. **Production-Ready**: Error handling, validation, and documentation included
