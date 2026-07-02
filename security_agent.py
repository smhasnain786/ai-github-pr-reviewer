from langchain_cohere import ChatCohere
from states.security_state import SecurityReview
from states.review_state import ReviewState
from dotenv import load_dotenv

load_dotenv()



async def security_agent(state: ReviewState) -> dict:
    model = ChatCohere(model="command-a-03-2025", temperature=0)
    structured_model = model.with_structured_output(SecurityReview)
    
    prompt = f"""
    You are a security reviewer analyzing a code diff for OWASP-aligned issues.
    Lines starting with + are additions. Lines starting with - are deletions.
    Flag security issues in ADDED lines as critical.
    Flag security issues in DELETED lines as informational only — they may be intentional fixes.
    Diff:
    {state["diff"]}
    
    Identify security vulnerabilities only. Ignore style and architecture.
    """
    
    result = await structured_model.ainvoke(prompt)
    return {"security_findings": result.model_dump()}


if __name__ == "__main__":
    security_agent({"diff": "diff --git a/sample.py b/sample.py\n+def add(a,b):\n+    return a+b"})    