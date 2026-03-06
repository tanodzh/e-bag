from fastapi import APIRouter
from app.routers.products import router as products_router
from app.routers.categories import router as categories_router
from app.api.v1.endpoints.search import router as search_router

router = APIRouter()

router.include_router(products_router, prefix="/products", tags=["products"])
router.include_router(categories_router, prefix="/categories", tags=["categories"])
router.include_router(search_router, prefix="/search", tags=["search"])