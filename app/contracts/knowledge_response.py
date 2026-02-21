from pydantic import BaseModel


class KnowledgeResponse(BaseModel):
    intent: str
    success: bool
    message: str
    confidence: float
    answer: str