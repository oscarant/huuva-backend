from fastapi.routing import APIRouter

from huuva_backend.web.api import views

# Create main API router
api_router = APIRouter()

# Alternatively, you can still include routers manually:
api_router.include_router(views.health_router)
api_router.include_router(views.order_router, prefix="/orders", tags=["orders"])
