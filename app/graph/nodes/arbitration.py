from app.core.local_arbitrator import CrossEncoderArbitrator
from app.core.state import ExecutionStatus
from app.core.errors import ErrorType


# Initialize once (avoid reloading model per call)
arbitrator = CrossEncoderArbitrator()


def arbitration_node(state: dict) -> dict:

    query = state.get("query")
    candidates = state.get("disambiguation_options", [])

    # --------------------------------------------------
    # SAFETY 1: No candidates
    # --------------------------------------------------
    if not candidates:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = ErrorType.ARBITRATION_FAILED
        return state

    # --------------------------------------------------
    # SAFETY 2: Only one candidate → accept directly
    # --------------------------------------------------
    if len(candidates) == 1:
        state["intent"] = candidates[0]
        state["status"] = ExecutionStatus.COMPLETED
        # Keep router confidence
        state["intent_confidence"] = state.get("intent_confidence", 0.0)
        return state

    # --------------------------------------------------
    # TRUE Arbitration (multiple candidates)
    # --------------------------------------------------
    intent, confidence = arbitrator.arbitrate(
        query,
        candidates
    )

    if intent is None:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = ErrorType.ARBITRATION_FAILED
        return state

    state["intent"] = intent
    state["intent_confidence"] = confidence
    state["confidence_band"] = "CROSS_ENCODER_RESOLVED"
    state["status"] = ExecutionStatus.COMPLETED

    return state