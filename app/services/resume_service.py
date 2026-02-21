from app.contracts.resume_response import ResumeResponse


class ResumeService:

    def handle(self, query: str) -> ResumeResponse:

        # Mock logic for now
        return ResumeResponse(
            intent="resume_help",
            success=True,
            message="Resume suggestions generated",
            confidence=0.88,
            suggestions="Consider adding quantified achievements and relevant keywords."
        )