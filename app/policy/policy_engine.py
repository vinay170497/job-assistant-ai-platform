class PolicyEngine:

    MAX_INPUT_LENGTH = 1500

    @staticmethod
    def validate(state: dict) -> dict:

        user_input = state.get("user_input", "")

        if len(user_input) > PolicyEngine.MAX_INPUT_LENGTH:
            state["status"] = "ERROR"
            state["error_message"] = "Input too long"
            return state

        if "hack" in user_input.lower():
            state["status"] = "ERROR"
            state["error_message"] = "Policy violation detected"
            return state

        return state