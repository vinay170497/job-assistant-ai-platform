from app.core.state import ExecutionStatus


class PolicyEngine:

    @staticmethod
    def validate(state: dict) -> dict:
        query = state.get("query")

        if query is None or not isinstance(query, str) or not query.strip():
            state["status"] = ExecutionStatus.ERROR
            state["error_type"] = "INVALID_INPUT"
            state["error_message"] = "Input cannot be empty."
            state["intent"] = None
            state["intent_confidence"] = None
            state["agent_output"] = None
            return state

        return state