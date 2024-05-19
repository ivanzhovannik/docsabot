import logging
from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException, FastAPI
from typing import Any, AsyncGenerator

from app.dependencies import OpenAIClientDependency, get_openai_client
from app.schema import UpdateDocsRequest
from config.config import settings
from core import bot

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    # create singleton
    get_openai_client()
    try:
        yield
    finally:
        # Clean up resources if necessary
        logger.info("Cleaning up client")

router = APIRouter(prefix="/ai", tags=["assistant"])

@router.post("/update-docs")
async def update_docs(request: UpdateDocsRequest, client: OpenAIClientDependency):
    github_token = settings.GITHUB.TOKEN 
    if not github_token:
        raise HTTPException(status_code=400, detail="GitHub token is required")
    
    # Use client singleton that is injected by Depends
    if not client:
        raise HTTPException(status_code=503, detail="Server is not ready")

    diff = request.diff
    logging.debug(f"Loaded DIFF: {diff}")
    repo_url = f"https://{github_token}@github.com/{request.repo}"
    logging.info(f"Target repository: {request.repo}")

    try:
        message = bot.update_docs(client, diff, repo_url, request.docs_path, request.model, request.temperature)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": message}
