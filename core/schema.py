from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class OpenAIRole(str, Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"

class OpenAIMessage(BaseModel):
    role: OpenAIRole = Field(..., examples=["user"])
    content: str

class OpenAIMessageQuery(BaseModel):
    messages: List[OpenAIMessage]

class DocumentUpdate(BaseModel):
    path: str
    old_content: str
    new_content: str

class UpdateDocsPayload(BaseModel):
    diff: str
    repo: str
    docs_path: str = "docs"
    model: str = "gpt-3.5-turbo"
    temperature: float = Field(1, ge=0, le=2)
    updates: Optional[List[DocumentUpdate]] = None