from fastapi import APIRouter, HTTPException
import os
import openai

from app.schema import UpdateDocsRequest
from core import bot

router = APIRouter(prefix="/ai", tags=["assistant"])

@router.post("/update-docs")
async def update_docs(request: UpdateDocsRequest):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        raise HTTPException(status_code=400, detail="GitHub token is required")

    diff = request.diff
    repo_url = f"https://{github_token}@github.com/{request.repo}"

    try:
        message = bot.update_docs(diff, repo_url, request.docs_path, request.model, request.temperature)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": message}
