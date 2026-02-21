from app.services.resume_service import ResumeService
from app.core.state import ExecutionStatus


def resume_agent_node(state: dict) -> dict:

    query = state.get("query")

    if not query:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "INVALID_QUERY"
        state["error_message"] = "Query cannot be empty"
        return state

    try:
        service = ResumeService()
        response = service.handle(query)

        state["agent_output"] = response.model_dump()
        state["status"] = ExecutionStatus.COMPLETED

        return state

    except Exception as e:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "RESUME_AGENT_ERROR"
        state["error_message"] = str(e)
        return state