import logging
from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException, FastAPI
from typing import Any, AsyncGenerator

from app.dependencies import OpenAIClientDependency, get_openai_client
from app.schema import UpdateDocsRequest, UpdateDocsPayload
from config.config import settings
from core.bot import update_docs

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
async def update_docs_endpoint(request: UpdateDocsRequest, client: OpenAIClientDependency):
    github_token = settings.GITHUB.TOKEN 
    if not github_token:
        raise HTTPException(status_code=400, detail="GitHub token is required")
    
    # Use client singleton that is injected by Depends
    if not client:
        raise HTTPException(status_code=503, detail="Server is not ready")

    logging.debug(f"Loaded DIFF: {request.diff}")
    repo_url = f"https://{github_token}@github.com/{request.repo}"
    logging.info(f"Target repository: {request.repo}")

    payload = UpdateDocsPayload(
        diff=request.diff,
        repo=repo_url,
        docs_path=request.docs_path,
        model=request.model,
        temperature=request.temperature
    )

    try:
        message = update_docs(client, payload)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": message, "updates": payload.updates}
