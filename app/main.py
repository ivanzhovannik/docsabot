import logging
from fastapi import FastAPI

from app.logs import setup_logging
from app.routers import ai, generic
from config.config import settings

logger = logging.getLogger(__name__)
setup_logging(settings.logging.level)

app = FastAPI(
    title=settings.openapi.title,
    description=settings.openapi.description,
    version=settings.openapi.version,
    contact=settings.openapi.contact,
    lifespan=ai.lifespan
)

app.include_router(ai.router)
app.include_router(generic.router)
