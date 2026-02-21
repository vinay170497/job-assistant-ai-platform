# app/graph/nodes/execution_node.py

from app.graph.nodes.job_agent import job_agent_node
from app.graph.nodes.resume_agent import resume_agent_node
from app.graph.nodes.rag_agent import rag_agent_node
from app.core.state import ExecutionStatus


def execution_node(state: dict) -> dict:

    intent = state.get("intent")

    if not intent:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "MISSING_INTENT"
        return state

    if intent == "job_search":
        return job_agent_node(state)

    elif intent == "resume_help":
        return resume_agent_node(state)

    elif intent == "knowledge_query":
        return rag_agent_node(state)

    else:
        state["status"] = ExecutionStatus.ERROR
        state["error_type"] = "UNSUPPORTED_INTENT"
        return state