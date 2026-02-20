from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class InvokeRequest(BaseModel):
    request_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)


class InvokeResponse(BaseModel):
    request_id: str
    status: str
    intent: Optional[str]
    intent_confidence: Optional[float]
    agent_output: Optional[Dict[str, Any]]
    error_type: Optional[str]
    error_message: Optional[str]