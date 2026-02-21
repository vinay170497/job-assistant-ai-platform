from app.contracts.knowledge_response import KnowledgeResponse


class KnowledgeService:

    def handle(self, query: str) -> KnowledgeResponse:

        # Mock RAG response
        return KnowledgeResponse(
            intent="knowledge_query",
            success=True,
            message="Knowledge retrieved successfully",
            confidence=0.90,
            answer="Here is the information related to your query."
        )