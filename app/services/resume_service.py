from app.contracts.resume_response import ResumeResponse


def handle_resume_help(user_input: str):

    return ResumeResponse(
        intent="resume_help",
        success=True,
        message="Resume analysis complete",
        confidence=0.82,
        improvement_suggestions=[
            "Add measurable achievements",
            "Use action verbs",
        ]
    )