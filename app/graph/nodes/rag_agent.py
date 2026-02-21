from app.services.knowledge_service import KnowledgeService
from app.core.state import ExecutionStatus


def rag_agent_node(state: dict) -> dict:

    query = state.get("query")

    if not query:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "INVALID_QUERY"
        state["error_message"] = "Query cannot be empty"
        return state

    try:
        service = KnowledgeService()
        response = service.handle(query)

        state["agent_output"] = response.model_dump()
        state["status"] = ExecutionStatus.COMPLETED

        return state

    except Exception as e:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "RAG_AGENT_ERROR"
        state["error_message"] = str(e)
        return state