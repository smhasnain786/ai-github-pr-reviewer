# main.py
from fastapi import FastAPI, Request, Header, HTTPException
import hmac
import hashlib
import os
from dotenv import load_dotenv
import httpx
from mainGraph import mainGraph
from github_client import post_pr_comment

load_dotenv()

app = FastAPI(title="PR Reviewer Webhook Receiver")

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_TOKEN = os.getenv("GH_PAT_TOKEN")


def format_review_comment(final_review: dict) -> str:
    overall_verdict=final_review.get("overall_verdict")

    security_findings=final_review.get("security_findings")
    style_findings=final_review.get("style_findings")
    architecture_findings=final_review.get("architecture_findings")

    comment_body = f"## 🤖 PR Review Summary\n**Overall Verdict:** {overall_verdict}\n"
    comment_body = f"**Summary:** {final_review.get("summary")}\n"
    security_findings_list = security_findings.get("findings", [])
    style_findings_list = style_findings.get("findings", [])
    architecture_findings_list = architecture_findings.get("findings", [])
    if security_findings_list:
        comment_body += "\n### 🔒 Security Findings\n"
        for security_finding in security_findings_list:
            # Get the issue text, use single quotes inside the brackets
            issue_text = security_finding.get("issue", "No description provided")
            # Use += to append to the string
            comment_body += f"- {issue_text}\n"
    if style_findings_list:
        comment_body += "\n### 🎨 Style Findings\n"
        for style_finding in style_findings_list:
            # Get the issue text, use single quotes inside the brackets
            issue_text = style_finding.get("issue", "No description provided")
            suggestion_text = style_finding.get("suggestion", "No suggestion provided")
            # Use += to append to the string
            comment_body += f"- {issue_text}\n"
            comment_body += f"Suggestion\n"
            comment_body += f"- {suggestion_text}\n"
    if architecture_findings_list:
        comment_body += "\n### 🏗️ Architecture Findings\n"
        for architecture_finding in architecture_findings_list:
            # Get the issue text, use single quotes inside the brackets
            issue_text = architecture_finding.get("issue", "No description provided")
            # Use += to append to the string
            comment_body += f"- {issue_text}\n"

    return comment_body


def is_reviewable_diff(diff_content: str) -> bool:
    """Skip binary files, lockfiles, and other non-reviewable diffs."""
    if "Binary files" in diff_content:
        return False
    if not diff_content.strip():
        return False
    return True    


async def fetch_pr_diff(diff_url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            diff_url,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3.diff"
            }
        )
        response.raise_for_status()
        return response.text


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify that the webhook actually came from GitHub, not someone spoofing it."""
    if not signature_header:
        return False

    hash_object = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None)
):
    payload_body = await request.body()

    # Verify the request is actually from GitHub
    if not verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    print(f"Received event: {x_github_event}")
    print(f"Action: {payload.get('action')}")

    if x_github_event == "pull_request" and payload.get("action") in ("opened", "synchronize"):
        pr = payload.get("pull_request", {})
        diff_url = pr.get("diff_url")

        pr_number=pr.get("number")
        repo_full_name = payload.get("repository", {}).get("full_name")
        diff_content = await fetch_pr_diff(diff_url)
        print(f"Diff length: {len(diff_content)} chars")
        print(diff_content[:500])  # preview first 500 chars
        if not is_reviewable_diff(diff_content):
            print("Skipping — non-reviewable diff")
            return {"status": "skipped", "reason": "non-reviewable diff"}
        try:
            results = await mainGraph(diff_content)
            result = await post_pr_comment(
                repo_full_name=repo_full_name,
                pr_number=pr_number,
                comment_body=format_review_comment(results["final_review"])
            )
            print(result["html_url"])
        except Exception as e:
            print(f"Review failed: {e}")
            # still return 200 so GitHub doesn't retry



    return {"status": "received", "event": x_github_event}


@app.get("/health")
async def health():
    return {"status": "ok"}