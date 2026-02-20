from app.contracts.job_response import JobSearchResponse, JobResult


def handle_job_search(user_input: str):

    dummy_jobs = [
        JobResult(
            title="Python Developer",
            location="Remote",
            company="TechCorp"
        )
    ]

    return JobSearchResponse(
        intent="job_search",
        success=True,
        message="Job search completed",
        confidence=0.85,
        jobs=dummy_jobs
    )