from typing import Optional, TypedDict


class JobFilters(TypedDict, total=False):
    role: Optional[str]
    location: Optional[str]
    experience: Optional[int]
    remote: Optional[bool]
    salary_min: Optional[int]