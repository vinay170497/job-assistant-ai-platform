from typing import TypedDict, Optional, List
from enum import Enum


class ExecutionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    COMPLETED = "COMPLETED"


class AgentState(TypedDict, total=False):
    # Core
    request_id: str
    user_input: str
    status: ExecutionStatus
    next_action: Optional[str]

    # Intent
    intent: Optional[str]
    intent_confidence: Optional[float]
    disambiguation_options: Optional[List[str]]

    # Output
    agent_output: Optional[str]

    # Error
    error_type: Optional[str]
    error_message: Optional[str]


def create_initial_state(request_id: str, user_input: str) -> AgentState:
    """
    Creates a fully initialized and schema-consistent state.
    This guarantees all expected keys exist from the start.
    """

    return {
        # Core
        "request_id": request_id,
        "user_input": user_input,
        "status": ExecutionStatus.ACTIVE,
        "next_action": None,

        # Intent
        "intent": None,
        "intent_confidence": 0.0,
        "disambiguation_options": None,

        # Output
        "agent_output": None,

        # Error
        "error_type": None,
        "error_message": None,
    }
