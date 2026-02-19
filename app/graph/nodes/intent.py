from app.core.state import AgentState, ExecutionStatus
from app.core.errors import ErrorType
from app.core.hybrid_router import HybridRouter


router = HybridRouter()
#registry = IntentRegistry()


def classify_intent_node(state: AgentState) -> AgentState:

    user_input = state.get("user_input", "").strip()

    if not user_input:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = ErrorType.INVALID_INPUT
        state["error_message"] = "Input cannot be empty."
        return state

    intent, score, band, disambiguation = router.classify(user_input)

    # ---- Ambiguity ----
    if band == "AMBIGUOUS":
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = ErrorType.DISAMBIGUATION_REQUIRED
        state["disambiguation_options"] = disambiguation
        return state

    # ---- Out of Scope ----
    if band == "OOS" or intent is None:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = ErrorType.OUT_OF_SCOPE
        return state

    # ---- Valid Intent ----
    state["intent"] = intent
    state["intent_confidence"] = score
    state["confidence_band"] = band
    state["status"] = ExecutionStatus.COMPLETED

    return state
