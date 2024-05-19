import os
from fastapi import APIRouter, Response
from fastapi.responses import FileResponse

from config.config import settings

router = APIRouter()

@router.get("/settings", tags=["Settings"])
def get_settings():
    settings_file_path = settings.openapi.settings_path
    if os.path.exists(settings_file_path):
        return FileResponse(settings_file_path)
    else:
        return Response(content="Settings file not found.", status_code=404)
