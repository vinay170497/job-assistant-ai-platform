# app/graph/nodes/intent.py

from app.core.hybrid_router import HybridRouter
from app.core.intent_registry import IntentRegistry
from app.core.llm_intent_fallback import OllamaIntentFallback
from app.core.state import ExecutionStatus
from app.core.telemetry import RoutingTelemetry


def classify_intent_node(state: dict) -> dict:

    query = state.get("query")
    telemetry = RoutingTelemetry()

    if not query:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "INVALID_INPUT"
        return state

    router = HybridRouter()
    fallback = OllamaIntentFallback()
    registry = IntentRegistry()
    allowed_intents = registry.get_all_intent_names()

    # ----------------------------
    # HYBRID CLASSIFICATION
    # ----------------------------
    hybrid_intent, hybrid_score, band, options = router.classify(query)

    telemetry.log({
        "query": query,
        "stage": "hybrid",
        "intent": hybrid_intent,
        "confidence": hybrid_score,
        "band": band
    })

    # HIGH confidence → accept immediately
    if band == "HIGH" and hybrid_intent:
        state["intent"] = hybrid_intent
        state["intent_confidence"] = hybrid_score
        state["confidence_band"] = band
        state["status"] = ExecutionStatus.ACTIVE

        telemetry.log({
            "query": query,
            "stage": "final",
            "decision": "HYBRID_HIGH_ACCEPTED"
        })

        return state

    # AMBIGUOUS → arbitration node
    if band == "AMBIGUOUS":
        state["status"] = ExecutionStatus.ARBITRATION_REQUIRED
        state["disambiguation_options"] = options

        telemetry.log({
            "query": query,
            "stage": "final",
            "decision": "ARBITRATION_REQUIRED",
            "options": options
        })

        return state

    # ----------------------------
    # LLM CLASSIFICATION (for MEDIUM/LOW/OOS)
    # ----------------------------
    llm_intent, llm_conf = fallback.classify(query, allowed_intents)

    telemetry.log({
        "query": query,
        "stage": "llm",
        "intent": llm_intent,
        "confidence": llm_conf
    })

    # ----------------------------
    # SUPERVISOR ARBITRATION LOGIC
    # ----------------------------

    # Case 1: Hybrid MEDIUM and agrees with LLM
    if band == "MEDIUM" and hybrid_intent == llm_intent:
        state["intent"] = hybrid_intent
        state["intent_confidence"] = hybrid_score
        state["confidence_band"] = "MEDIUM_CONFIRMED"
        state["status"] = ExecutionStatus.ACTIVE

        telemetry.log({
            "query": query,
            "stage": "final",
            "decision": "HYBRID_MEDIUM_CONFIRMED"
        })

        return state

    # Case 2: Hybrid MEDIUM but disagreement → choose higher confidence
    if band == "MEDIUM" and llm_intent and llm_intent != hybrid_intent:
        if llm_conf > hybrid_score:
            chosen_intent = llm_intent
            chosen_conf = llm_conf
            source = "LLM_OVERRULED"
        else:
            chosen_intent = hybrid_intent
            chosen_conf = hybrid_score
            source = "HYBRID_RETAINED"

        state["intent"] = chosen_intent
        state["intent_confidence"] = chosen_conf
        state["confidence_band"] = source
        state["status"] = ExecutionStatus.ACTIVE

        telemetry.log({
            "query": query,
            "stage": "final",
            "decision": source
        })

        return state

    # Case 3: Hybrid LOW or OOS but LLM confident
    if band in ["LOW", "OOS"] and llm_intent and llm_conf >= 0.60:
        state["intent"] = llm_intent
        state["intent_confidence"] = llm_conf
        state["confidence_band"] = "LLM_RECOVERY"
        state["status"] = ExecutionStatus.ACTIVE

        telemetry.log({
            "query": query,
            "stage": "final",
            "decision": "LLM_RECOVERY"
        })

        return state

    # ----------------------------
    # Otherwise → OUT OF SCOPE
    # ----------------------------
    state["status"] = ExecutionStatus.ERROR
    state["error_type"] = "OUT_OF_SCOPE"
    state["intent"] = None
    state["intent_confidence"] = 0.0

    telemetry.log({
        "query": query,
        "stage": "final",
        "decision": "OUT_OF_SCOPE"
    })

    return state