from pydantic import BaseModel, Field

class UpdateDocsRequest(BaseModel):
    diff: str
    repo: str
    docs_path: str = "docs"  # Default to 'docs' if not provided
    model: str = "gpt-3.5-turbo"  # Default model
    temperature: float = Field(1, ge=0, le=2)  # Default temperature with constraints