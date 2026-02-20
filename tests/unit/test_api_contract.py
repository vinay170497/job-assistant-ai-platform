import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.core.state import ExecutionStatus


# ---------------------------
# Mock Graph for Testing
# ---------------------------
class MockGraph:
    def invoke(self, payload: dict):
        return {
            "request_id": payload["request_id"],
            "status": ExecutionStatus.COMPLETED,
            "intent": "job_search",
            "intent_confidence": 0.85,
            "agent_output": {
                "intent": "job_search",
                "success": True,
                "message": "Job search completed",
                "confidence": 0.85,
                "jobs": [
                    {
                        "title": "Python Developer",
                        "location": "Remote",
                        "company": "TechCorp"
                    }
                ]
            },
            "error_type": None,
            "error_message": None,
        }


def override_get_graph():
    return MockGraph()


app.dependency_overrides = {}
app.dependency_overrides[
    app.dependency_overrides.get
] = None


# Override graph dependency
from app.api.main import get_graph
app.dependency_overrides[get_graph] = override_get_graph


client = TestClient(app, raise_server_exceptions=True)


# ---------------------------
# Tests
# ---------------------------
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_invoke_success():
    payload = {
        "request_id": "123",
        "query": "Find python developer jobs"
    }

    response = client.post("/invoke", json=payload)
    assert response.status_code == 200

    data = response.json()

    assert data["request_id"] == "123"
    assert data["status"] == "COMPLETED"
    assert data["intent"] == "job_search"
    assert isinstance(data["intent_confidence"], float)
    assert data["agent_output"] is not None
    assert data["error_type"] is None
    assert data["error_message"] is None


def test_invoke_invalid_payload():
    payload = {
        "request_id": "",
        "query": ""
    }

    response = client.post("/invoke", json=payload)
    assert response.status_code == 422


def test_invoke_missing_field():
    payload = {
        "request_id": "123"
    }

    response = client.post("/invoke", json=payload)
    assert response.status_code == 422


def test_process_time_header_present():
    payload = {
        "request_id": "999",
        "query": "Find backend jobs"
    }

    response = client.post("/invoke", json=payload)
    assert "X-Process-Time" in response.headers