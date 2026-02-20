from app.contracts.knowledge_response import KnowledgeResponse


def handle_knowledge_query(user_input: str):

    return KnowledgeResponse(
        intent="knowledge_query",
        success=True,
        message="Knowledge response generated",
        confidence=0.88,
        answer="Machine learning is a subset of AI..."
    )