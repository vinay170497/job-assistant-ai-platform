from app.graph.builder import build_graph
from app.core.state import ExecutionStatus


def test_all_cases():

    graph = build_graph()

    test_cases = [
        {"input": "", "expected_error": True},
        {"input": "hi", "expected_error": True},
        {"input": "find python developer jobs", "expected_intent": "job_search"},
        {"input": "current openings in data science", "expected_intent": "job_search"},
        {"input": "improve my resume", "expected_intent": "resume_help"},
        {"input": "how does machine learning work", "expected_intent": "knowledge_query"},
        {"input": "job resume help", "expected_intent": "resume_help"},
        {"input": "tell me a random joke", "expected_error": True},
    ]

    for case in test_cases:
        result = graph.invoke({
            "request_id": "test",
            "user_input": case["input"],
            "status": "ACTIVE"
        })

        if case.get("expected_error"):
            assert result["status"] != ExecutionStatus.COMPLETED
            #assert result["status"] != "COMPLETED"
        else:
            print(f"DEBUG: Result keys: {result.keys()} | Full result: {result}")
            assert result["intent"] == case["expected_intent"]
            assert result["status"] == "COMPLETED"
