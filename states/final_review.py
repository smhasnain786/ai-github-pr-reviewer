from pydantic import BaseModel, Field
from typing import Literal

class FinalReview(BaseModel):
    overall_verdict: Literal["approve", "request_changes"]
    summary: str = Field(description="A short human-readable summary of the review")
    security_findings: list
    style_findings: list
    architecture_findings: list