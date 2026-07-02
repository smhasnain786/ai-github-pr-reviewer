from langchain_cohere import ChatCohere
from states.architecture_state import ArchitectureReview
from states.review_state import ReviewState
from dotenv import load_dotenv

load_dotenv()



async def architecture_agent(state: ReviewState) -> dict:
    model = ChatCohere(model="command-a-03-2025", temperature=0)
    structured_model = model.with_structured_output(ArchitectureReview)
    
    prompt = f"""
        You are a architecture reviewer analyzing a code diff for architecture issues only.

        Diff:
        {state["diff"]}

        STRICT SCOPE — only flag issues in these categories:
        - tight coupling between unrelated components
        - missing separation of concerns (e.g. business logic mixed with I/O or presentation)
        - single responsibility violations (a function/class doing too many unrelated things)
        - missing abstractions (repeated logic that should be extracted)
        - hardcoded values that should be configuration

        DO NOT mention security vulnerabilities, injection risks, or unsafe function usage in any form — even reframed as "coupling," "portability," or "architecture" concerns.
        If a line involves os.system, eval, exec, subprocess, SQL queries, or any function that executes external input, do not comment on that line at all, regardless of framing. Skip it entirely.
        
        """
    
    result = await structured_model.ainvoke(prompt)
    return {"architecture_findings": result.model_dump()}


if __name__ == "__main__":
    architecture_agent({"diff": "diff --git a/sample.py b/sample.py\n+def add(a,b):\n+    return a+b"})    