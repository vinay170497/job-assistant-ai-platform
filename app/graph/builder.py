from langgraph.graph import StateGraph, END
from app.core.state import AgentState, ExecutionStatus
from app.graph.nodes.intent import classify_intent_node


def normalize_state_before_exit(state: AgentState) -> AgentState:
    """
    Final guardrail node.
    Ensures state schema is complete and safe before graph termination.
    """

    state.setdefault("intent", None)
    state.setdefault("intent_confidence", 0.0)
    state.setdefault("disambiguation_options", None)
    state.setdefault("agent_output", None)
    state.setdefault("error_type", None)
    state.setdefault("error_message", None)

    # Safety: ensure status is valid
    if "status" not in state or state["status"] is None:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "STATE_VALIDATION_ERROR"
        state["error_message"] = "Missing execution status."

    return state


def build_graph():
    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("intent_classifier", classify_intent_node)
    builder.add_node("finalize", normalize_state_before_exit)

    # Entry
    builder.set_entry_point("intent_classifier")

    # Flow
    builder.add_edge("intent_classifier", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()
