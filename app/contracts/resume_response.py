from app.contracts.base_response import BaseAgentResponse


class ResumeResponse(BaseAgentResponse):
    improvement_suggestions: list[str] = []