from .auth import router as auth_router
from .users import router as users_router
from .materials import router as materials_router
from .inventory import router as inventory_router
from .sales import router as sales_router
from .purchase import router as purchase_router
from .production import router as production_router
from .quality import router as quality_router

__all__ = [
    "auth_router",
    "users_router",
    "materials_router",
    "inventory_router",
    "sales_router",
    "purchase_router",
    "production_router",
    "quality_router",
]