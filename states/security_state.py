from pydantic import BaseModel,Field


class SecurityFinding(BaseModel):
    issue: str = Field(description="...")
    severity: str = Field(description="critical, high, medium, low, or informational — use informational for issues found in deleted lines")
    line_reference: str = Field(description="...")

class SecurityReview(BaseModel):
    findings: list[SecurityFinding]
    verdict: str = Field(description="approve or request_changes")