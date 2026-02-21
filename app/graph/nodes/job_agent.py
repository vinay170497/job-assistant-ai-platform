from app.services.job_search_service import JobSearchService
from app.core.state import ExecutionStatus


def job_agent_node(state: dict) -> dict:
    """
    Job Agent Node:
    - Uses JobSearchService
    - Updates state with structured contract response
    - Does NOT change service interface
    """

    query = state.get("query")

    if not query:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "INVALID_QUERY"
        state["error_message"] = "Query cannot be empty"
        return state

    try:
        service = JobSearchService()

        # Call service using original contract structure
        response = service.handle(query)

        # Store structured response
        state["agent_output"] = response.model_dump()

        state["status"] = ExecutionStatus.COMPLETED

        return state

    except Exception as e:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "JOB_AGENT_ERROR"
        state["error_message"] = str(e)
        return state