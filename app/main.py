from fastapi import FastAPI
from config.config import settings
from app.routers import ai, generic

app = FastAPI(
    title=settings.openapi.title,
    description=settings.openapi.description,
    version=settings.openapi.version,
    contact=settings.openapi.contact
)

app.include_router(ai.router)
app.include_router(generic.router)
