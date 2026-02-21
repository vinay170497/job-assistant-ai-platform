from pydantic import BaseModel
from typing import Optional


class ResumeResponse(BaseModel):
    intent: str
    success: bool
    message: str
    confidence: float
    suggestions: Optional[str] = None