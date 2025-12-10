"""
Routers API FastAPI.
"""

from .export import router as export_router
from .haikus import router as haikus_router
from .quotes import router as quotes_router

__all__ = ["quotes_router", "haikus_router", "export_router"]
