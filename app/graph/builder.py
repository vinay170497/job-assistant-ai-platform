from langgraph.graph import StateGraph, END
from app.core.state import AgentState, ExecutionStatus
from app.graph.nodes.intent import classify_intent_node
from app.graph.nodes.arbitration import arbitration_node
from app.graph.nodes.execution_node import execution_node
from app.policy.policy_engine import PolicyEngine


def normalize_state_before_exit(state: AgentState) -> AgentState:
    """
    Final guardrail node.
    Ensures state schema is complete and safe before graph termination.
    """

    state.setdefault("intent", None)
    state.setdefault("intent_confidence", 0.0)
    state.setdefault("confidence_band", None)
    state.setdefault("disambiguation_options", None)
    state.setdefault("agent_output", None)
    state.setdefault("error_type", None)
    state.setdefault("error_message", None)

    # Safety: ensure status exists
    if "status" not in state or state["status"] is None:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "STATE_VALIDATION_ERROR"
        state["error_message"] = "Missing execution status."

    return state


def build_graph():
    builder = StateGraph(AgentState)
    
    def policy_node(state: dict) -> dict:
        return PolicyEngine.validate(state)
    # -------------------------
    # Nodes
    # -------------------------
    builder.add_node("intent_classifier", classify_intent_node)
    builder.add_node("arbitration", arbitration_node)
    builder.add_node("execution", execution_node)
    builder.add_node("finalize", normalize_state_before_exit)
    builder.add_node("policy_check", policy_node)

    # -------------------------
    # Entry
    # -------------------------
    
    
    builder.set_entry_point("policy_check")
    builder.add_edge("policy_check", "intent_classifier")
    
    # -------------------------
    # Conditional Routing
    # -------------------------
    builder.add_conditional_edges(
    "intent_classifier",
    lambda state: (
        "arbitration"
        if state.get("status") == ExecutionStatus.ARBITRATION_REQUIRED
        else "execution"
    )
)

    # After arbitration → execution → finalize
    builder.add_edge("arbitration", "execution")
    builder.add_edge("execution", "finalize")

    # Final exit
    builder.add_edge("finalize", END)

    return builder.compile()