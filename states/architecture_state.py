from pydantic import BaseModel,Field


class ArchitectureFinding(BaseModel):
    issue: str = Field(description="...")
    severity: str = Field(description="low, medium, high, critical")
    line_reference: str = Field(description="...")

class ArchitectureReview(BaseModel):
    findings: list[ArchitectureFinding]
    verdict: str = Field(description="approve or request_changes")