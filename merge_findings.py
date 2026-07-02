from langchain_cohere import ChatCohere
from states.final_review import FinalReview
from states.review_state import ReviewState
from dotenv import load_dotenv

load_dotenv()



async def merge_findings(state: ReviewState) -> dict:
    
    # print((state))
    
    security_findings=state.get("security_findings")
    security_finding_verdict=security_findings.get("verdict")

    style_findings=state.get("style_findings")
    style_findings_verdict=style_findings.get("verdict")

    architecture_findings=state.get("architecture_findings")
    architecture_findings_verdict=architecture_findings.get("verdict")
    
    if "request_changes" in (security_finding_verdict, style_findings_verdict, architecture_findings_verdict):
        overall_verdict = "request_changes"
    else:
        overall_verdict = "approve"
        
    requesting_categories = []
    if security_finding_verdict == "request_changes":
        requesting_categories.append("security")
    if style_findings_verdict == "request_changes":
        requesting_categories.append("style")
    if architecture_findings_verdict == "request_changes":
        requesting_categories.append("architecture")

    summary = f"Changes requested by: {', '.join(requesting_categories)}." if requesting_categories else "All checks passed."    

    final_review = {
        "overall_verdict": overall_verdict,
        "summary": summary,
        "security_findings": security_findings,
        "style_findings": style_findings,
        "architecture_findings": architecture_findings,
    }

    return {"final_review": final_review}
    


if __name__ == "__main__":
    merge_findings({"diff": "diff --git a/sample.py b/sample.py\n+def add(a,b):\n+    return a+b"})    