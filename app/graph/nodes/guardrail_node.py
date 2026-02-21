from app.core.state import ExecutionStatus


CONFIDENCE_THRESHOLD = 0.5


def guardrail_node(state: dict) -> dict:

    intent = state.get("intent")
    confidence = state.get("intent_confidence")
    query = state.get("query")

    if not query or not query.strip():
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "EMPTY_QUERY"
        return state

    if not intent:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "INTENT_NOT_DETECTED"
        return state

    if confidence is not None and confidence < CONFIDENCE_THRESHOLD:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "LOW_INTENT_CONFIDENCE"
        return state

    return state