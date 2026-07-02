# github_client.py
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GH_PAT_TOKEN = os.getenv("GH_PAT_TOKEN")


async def post_pr_comment(repo_full_name: str, pr_number: int, comment_body: str):
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"token {GH_PAT_TOKEN}",
                "Accept": "application/vnd.github+json"
            },
            json={"body": comment_body}
        )
        
        if response.status_code != 201:
            print(f"Status: {response.status_code}")
            print(f"Response body: {response.text}")  # <-- this is what we actually need
        
        response.raise_for_status()
        return response.json()