from pydantic import BaseModel
from typing import Optional, List


class JobResult(BaseModel):
    title: str
    location: Optional[str]
    company: Optional[str]
    apply_url: Optional[str]


class JobSearchResponse(BaseModel):
    intent: str
    success: bool
    message: str
    confidence: float
    jobs: List[JobResult]