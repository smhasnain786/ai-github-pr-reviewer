# AI GitHub PR Code Reviewer

An event-driven, multi-agent AI system that automatically reviews GitHub Pull Requests and posts structured feedback as comments.

## How It Works

A GitHub webhook fires on every PR open or push event. The system fetches the diff, runs three specialized AI agents in parallel using LangGraph, merges their findings, and posts a structured review comment back to the PR — all without human intervention.

```
GitHub PR Event
      ↓
Webhook (FastAPI) — signature verified
      ↓
Diff Fetched (GitHub API)
      ↓
      ├── Security Agent ──┐
      ├── Style Agent ─────┼── Parallel (LangGraph StateGraph)
      └── Architecture ────┘
                ↓
         Merge Findings
                ↓
    PR Comment Posted (GitHub API)
```

## Agents

**Security Agent** — flags OWASP-aligned vulnerabilities. Distinguishes between issues in added lines (critical) and deleted lines (informational). Ignores style and architecture concerns.

**Style Agent** — checks naming conventions, formatting, documentation, duplication, and complexity. Explicitly excludes security issues even when they overlap stylistically.

**Architecture Agent** — identifies single responsibility violations, tight coupling, missing abstractions, and hardcoded configuration values.

Each agent runs independently and concurrently. The merge step determines the overall verdict: if any agent requests changes, the PR is flagged.

## Tech Stack

- **FastAPI** — webhook receiver with GitHub signature verification
- **LangGraph** — parallel multi-agent orchestration via `StateGraph`
- **Cohere** (`command-a-03-2025`) — LLM powering all three agents
- **Pydantic** — structured output schemas per agent
- **httpx** — async GitHub API client

## Project Structure

```
├── main.py                  # FastAPI app, webhook handler, diff fetcher
├── mainGraph.py             # LangGraph StateGraph definition
├── security_agent.py        # Security review agent
├── style_agent.py           # Style review agent
├── architecture_agent.py    # Architecture review agent
├── merge_findings.py        # Combines agent outputs into final verdict
├── github_client.py         # Posts review comment to GitHub PR
└── states/
    ├── review_state.py      # Shared LangGraph state (TypedDict)
    ├── security_state.py    # SecurityFinding, SecurityReview schemas
    ├── style_state.py       # StyleFinding, StyleReview schemas
    ├── architecture_state.py # ArchitectureFinding, ArchitectureReview schemas
    └── final_review.py      # FinalReview schema
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/smhasnain786/ai-github-pr-reviewer.git
cd ai-github-pr-reviewer
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

Copy `.env.example` to `.env` and fill in:
```
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GH_PAT_TOKEN=your_github_personal_access_token
COHERE_API_KEY=your_cohere_api_key
```

> **Important:** Do not use `GITHUB_TOKEN` as the variable name inside GitHub Codespaces — it is auto-injected by the environment with restricted permissions and will silently override your PAT.

**4. Run the server**
```bash
uvicorn main:app --reload --port 8000
```

**5. Expose locally with ngrok**
```bash
ngrok http 8000
```

**6. Register the webhook on your GitHub repo**

- Payload URL: `https://your-ngrok-url/webhook/github`
- Content type: `application/json`
- Secret: same value as `GITHUB_WEBHOOK_SECRET` in `.env`
- Events: Pull requests only

## Example Review Comment

```
## 🤖 PR Review Summary
**Overall Verdict:** request_changes

### 🔒 Security Findings
- Hardcoded API token in the source code (informational — found in deleted line, likely intentional fix)

### 🎨 Style Findings
- Missing docstring for new function
  Suggestion: Add a docstring describing purpose, parameters, and return value

### 🏗️ Architecture Findings
- Math module imported inside function body — move to module level to avoid tight coupling
```

## Design Decisions

**Why parallel agents instead of one agent?** A single agent asked to review for security, style, and architecture simultaneously produces unfocused, lower-quality findings. Specialised agents with explicit scope boundaries produce more accurate, category-specific feedback.

**Why LangGraph instead of `asyncio.gather`?** LangGraph's `StateGraph` handles shared state merging across parallel nodes natively. With `asyncio.gather`, you write the merge logic manually. The graph also makes the execution flow explicit and debuggable.

**Why does the system return 200 even on internal errors?** GitHub retries failed webhook deliveries aggressively. Returning 500 on a transient LLM timeout would trigger duplicate reviews. Errors are logged and the webhook always acknowledges receipt.

**Why `informational` severity for deleted-line findings?** A diff removing a hardcoded secret is evidence the secret existed — worth logging — but not a reason to block the PR. Severity reflects the action required, not just the presence of the pattern.