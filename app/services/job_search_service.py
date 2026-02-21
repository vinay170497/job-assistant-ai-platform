import os
import requests
from typing import List
from app.contracts.job_response import JobSearchResponse, JobResult


class JobSearchService:

    ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

    def __init__(self):
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID")
        self.adzuna_app_key = os.getenv("ADZUNA_APP_KEY")
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")

    # -------------------------
    # PUBLIC ENTRY
    # -------------------------
    def handle(self, query: str) -> JobSearchResponse:

        try:
            adzuna_jobs = self.call_adzuna(query)
            rapid_jobs = self.call_rapidapi(query)

            combined = adzuna_jobs + rapid_jobs
            deduped = self.deduplicate(combined)

            top_jobs = deduped[:5]

            return JobSearchResponse(
                intent="job_search",
                success=True,
                message="Job search completed successfully",
                confidence=0.93,
                jobs=top_jobs
            )

        except Exception as e:
            return JobSearchResponse(
                intent="job_search",
                success=False,
                message=f"Job provider error: {str(e)}",
                confidence=0.0,
                jobs=[]
            )

    # -------------------------
    # ADZUNA API
    # -------------------------
    def call_adzuna(self, query: str) -> List[JobResult]:

        params = {
            "app_id": self.adzuna_app_id,
            "app_key": self.adzuna_app_key,
            "results_per_page": 5,
            "what": query,
            "content-type": "application/json"
        }

        response = requests.get(self.ADZUNA_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        jobs = []

        for item in data.get("results", []):

            jobs.append(
                JobResult(
                    title=item.get("title"),
                    location=item.get("location", {}).get("display_name"),
                    company=item.get("company", {}).get("display_name"),
                    apply_url=item.get("redirect_url")
                )
            )

        return jobs

    # -------------------------
    # RAPIDAPI (Example Endpoint)
    # -------------------------
    def call_rapidapi(self, query: str) -> List[JobResult]:

        if not self.rapidapi_key:
            return []

        url = "https://jsearch.p.rapidapi.com/search"

        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

        params = {
            "query": query,
            "num_pages": 1
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        jobs = []

        for item in data.get("data", []):

            jobs.append(
                JobResult(
                    title=item.get("job_title"),
                    location=item.get("job_city"),
                    company=item.get("employer_name"),
                    apply_url=item.get("job_apply_link")
                )
            )

        return jobs

    # -------------------------
    # DEDUPLICATION
    # -------------------------
    def deduplicate(self, jobs: List[JobResult]) -> List[JobResult]:

        seen = set()
        unique_jobs = []

        for job in jobs:
            identifier = (job.title, job.company, job.location)

            if identifier not in seen:
                seen.add(identifier)
                unique_jobs.append(job)

        return unique_jobs