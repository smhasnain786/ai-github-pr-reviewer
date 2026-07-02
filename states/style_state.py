from pydantic import BaseModel,Field


class StyleFinding(BaseModel):
    issue: str = Field(description="The specific style or readability issue found")
    category: str = Field(description="naming, formatting, duplication, complexity, or documentation")
    suggestion: str = Field(description="A concrete suggestion to fix this issue")
    line_reference: str = Field(description="The relevant line or code snippet")

class StyleReview(BaseModel):
    findings: list[StyleFinding]
    verdict: str = Field(description="approve or request_changes")