from pydantic import BaseModel
from typing import Optional, List


class BaseAgentResponse(BaseModel):
    intent: str
    success: bool
    message: str
    confidence: Optional[float] = None