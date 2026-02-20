# app/graph/nodes/execution_node.py

from app.services.job_search_service import handle_job_search
from app.services.resume_service import handle_resume_help
from app.services.knowledge_service import handle_knowledge_query


def execution_node(state: dict) -> dict:

    intent = state.get("intent")

    if intent == "job_search":
        response = handle_job_search(state["user_input"])

    elif intent == "resume_help":
        response = handle_resume_help(state["user_input"])

    elif intent == "knowledge_query":
        response = handle_knowledge_query(state["user_input"])

    else:
        return state

    state["agent_output"] = response.model_dump()
    return state