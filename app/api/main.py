from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
import logging
import time

from app.graph.builder import build_graph
from app.api.schemas import InvokeRequest, InvokeResponse
from app.core.state import ExecutionStatus


# --------------------------
# Logging Configuration
# --------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job_assistant_api")


# --------------------------
# Lifespan Handler (Modern FastAPI)
# --------------------------
_graph_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graph_instance
    _graph_instance = build_graph()  # preload graph on startup
    yield
    # optional shutdown cleanup here


app = FastAPI(
    title="Job Assistant AI Platform",
    lifespan=lifespan
)


def get_graph():
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = build_graph()
    return _graph_instance


# --------------------------
# Middleware for Logging
# --------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"completed_in={process_time:.4f}s "
        f"status_code={response.status_code}"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# --------------------------
# Global Exception Handler
# --------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={
            "request_id": "unknown",
            "status": ExecutionStatus.ERROR.value,
            "intent": None,
            "intent_confidence": None,
            "agent_output": None,
            "error_type": "INTERNAL_SERVER_ERROR",
            "error_message": "Unexpected system error",
        },
    )


# --------------------------
# Health Endpoint
# --------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}


# --------------------------
# Invoke Endpoint (Async Safe)
# --------------------------
@app.post("/invoke", response_model=InvokeResponse)
async def invoke(
    request: InvokeRequest,
    graph=Depends(get_graph)
):
    # Normalize input state explicitly
    initial_state = {
        "request_id": request.request_id,
        "query": request.query.strip(),
        "intent": None,
        "intent_confidence": None,
        "status": None,
        "agent_output": None,
        "error_type": None,
        "error_message": None,
    }

    result = await run_in_threadpool(
        graph.invoke,
        initial_state
    )

    status_value = (
        result.get("status").value
        if hasattr(result.get("status"), "value")
        else result.get("status")
    )

    return InvokeResponse(
        request_id=result.get("request_id"),
        status=status_value,
        intent=result.get("intent"),
        intent_confidence=result.get("intent_confidence"),
        agent_output=result.get("agent_output"),
        error_type=result.get("error_type"),
        error_message=result.get("error_message"),
    )