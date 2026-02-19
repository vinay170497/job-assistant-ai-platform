import logging


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def log_transition(request_id: str, from_state: str, to_state: str):
    logging.info(
        f"[REQUEST {request_id}] STATE TRANSITION: {from_state} → {to_state}"
    )


def log_error(request_id: str, error_type: str, message: str):
    logging.error(
        f"[REQUEST {request_id}] ERROR: {error_type} | {message}"
    )
