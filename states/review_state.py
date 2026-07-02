from typing import TypedDict

class ReviewState(TypedDict):
    diff: str
    security_findings: dict
    style_findings: dict
    architecture_findings: dict
    final_review: dict