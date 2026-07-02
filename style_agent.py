from langchain_cohere import ChatCohere
from states.style_state import StyleReview
from states.review_state import ReviewState
from dotenv import load_dotenv

load_dotenv()



async def style_agent(state: ReviewState) -> dict:
    model = ChatCohere(model="command-a-03-2025", temperature=0)
    structured_model = model.with_structured_output(StyleReview)
    
    prompt = f"""
        You are a style reviewer analyzing a code diff for readability and maintainability issues only.

        Diff:
        {state["diff"]}

        STRICT SCOPE — only flag issues in these categories:
        - naming conventions
        - function/file length and complexity
        - code duplication
        - formatting and whitespace
        - missing or unclear documentation

        DO NOT mention security vulnerabilities, injection risks, or unsafe function usage — even if you notice them. 
        A separate security reviewer handles that. If a line has a security issue but no style issue, do not include it in your findings at all.
        DO NOT mention security vulnerabilities, injection risks, or unsafe function usage in any form — even reframed as "maintainability" or "clarity" concerns. 
        If a line involves os.system, eval, exec, subprocess, SQL queries, or any function that executes external input, do not comment on that line at all, regardless of framing. Skip it entirely.
        """
    
    result = await structured_model.ainvoke(prompt)
    return {"style_findings": result.model_dump()}


if __name__ == "__main__":
    style_agent({"diff": "diff --git a/sample.py b/sample.py\n+def add(a,b):\n+    return a+b"})    