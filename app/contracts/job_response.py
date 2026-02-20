from pydantic import BaseModel
from typing import List
from app.contracts.base_response import BaseAgentResponse


class JobResult(BaseModel):
    title: str
    location: str
    company: str


class JobSearchResponse(BaseAgentResponse):
    jobs: List[JobResult] = []