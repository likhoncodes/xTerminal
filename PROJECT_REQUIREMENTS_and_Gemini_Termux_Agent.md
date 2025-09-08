# xTerminal — Project Requirements & Gemini Agent for Termux

## TL;DR

Create a Termux-ready AI agent ("xTerminal Agent") that uses a Gemini-compatible HTTP API for inference.

Repo will include: PROJECT_REQUIREMENTS.md, agent/ (Python FastAPI agent), scripts/ (install & start scripts), .env.example, requirements.txt, and termux/ notes for running as a background service.

Deliverables: reproducible Termux setup steps, secure environment handling, a lightweight REST wrapper to Gemini, a CLI wrapper for interactive terminal usage, and simple automated startup.

---

## Purpose

This document specifies requirements and a concrete implementation plan to add a Gemini-based AI agent to the https://github.com/likhoncodes/xTerminal repository and make it runnable inside Termux on Android devices. The agent provides a shell-like assistant that can execute permitted shell commands and return structured outputs while preserving safety and security.

## Goals

1. Minimal, robust Termux-compatible stack (Python 3.11+, pip, optionally Node.js).
2. Lightweight HTTP agent acting as a local bridge between terminal UI and Gemini API.
3. Safe command-execution policy and audit logging.
4. Startup scripts to run the agent persistently in Termux.
5. CI-friendly test script for integration.

## High-level architecture

termux (device)
xTerminal agent (FastAPI, Python) ← communicates with → Gemini (remote model endpoint)
xTerminal CLI (local shell client; small Python script) → HTTP → agent
scripts/ manage install & runtime configuration

## Files to add to repo

- `PROJECT_REQUIREMENTS_and_Gemini_Termux_Agent.md` (this file)
- `agent/` directory
  - `app.py` — FastAPI application that exposes /health, /chat, /exec endpoints
  - `cli_client.py` — small interactive CLI to send user messages and show responses
  - `requirements.txt` — Python package dependencies
  - `.env.example` — example environment variables
  - `README_AGENT.md` — quick start for the agent
- `scripts/`
  - `termux_install.sh` — installs dependencies on Termux and sets up venv
  - `termux_start.sh` — start/stop wrapper for Termux background run (tmux or termux-service)
- `termux/` notes for Termux-specific tips and service wrappers
- `tests/` minimal integration tests (can run on desktop/dev)

## Requirements — Software

- Termux (latest build)
- Python 3.11+ installed in Termux (pkg install python)
- pip
- git
- optionally: tmux or proot (for background running)

## Environment variables (place in .env — do NOT commit secrets)

GEMINI_API_URL=https://api.example.com/v1/gemini
GEMINI_API_KEY=sk-...           # required
AGENT_PORT=8080
ALLOWED_SHELL_CMDS=ls,cat,pwd,whoami,df,free
LOG_PATH=./agent/logs/agent.log
MAX_RESPONSE_TOKENS=800

## Security and safety notes

- Never commit API keys or .env to the repository. Use .gitignore to exclude .env and agent/logs/.
- The agent provides a controlled /exec endpoint — only commands in ALLOWED_SHELL_CMDS may be executed.
- All /exec calls are audited to LOG_PATH with timestamp, user, command, and exit code.
- Rate-limit the /chat endpoint to avoid abuse (example: 10 requests/min per IP) — the provided sample includes a simple in-memory limiter.

## Implementation (concise)

> The repo will include a ready-to-run Python example. Below are the key snippets (already placed in the agent/ folder in this plan):

### requirements.txt
```
fastapi==0.95.2
uvicorn[standard]==0.22.0
python-dotenv==1.0.0
httpx==0.24.0
pydantic==2.5.1
aiofiles==23.1.0
```

### app.py — FastAPI agent outline
- `/health` — basic ready check
- `/chat` — POST: { "input": "..." } => forwards to Gemini API and streams/returns response
- `/exec` — POST: { "cmd": "ls -la" } => validate command against whitelist and run with subprocess.run (timeout enforced) and return stdout/stderr

### cli_client.py — interactive CLI to send messages to /chat and /exec

### termux_install.sh — example setup actions:
```bash
pkg update && pkg upgrade -y
pkg install python git tmux -y
git clone https://github.com/likhoncodes/xTerminal.git
cd xTerminal/agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example -> .env and add GEMINI_API_KEY/GEMINI_API_URL
```

### termux_start.sh — start agent
```bash
#!/data/data/com.termux/files/usr/bin/bash
source ./agent/.venv/bin/activate
export $(grep -v '^#' agent/.env | xargs)
# run with tmux so it can be backgrounded
tmux new -d -s xterminal "uvicorn agent.app:app --host 0.0.0.0 --port ${AGENT_PORT} --log-level info"
```

## Gemini integration pattern

The agent calls the Gemini-compatible endpoint via `httpx.AsyncClient`. The request/response pattern follows a simple prompt-based approach: send user message + context, request max tokens, temperature, streaming optional. The agent converts Gemini responses into structured JSON before returning to the CLI.

> NOTE: Replace GEMINI_API_URL with your provider's endpoint. Example request body (pseudo):

```json
{
  "model": "gemini-pro",
  "input": "<user prompt>",
  "max_tokens": 512
}
```

## Example minimal app.py behaviors (already in agent folder):

- Validate incoming JSON with Pydantic models.
- Use `httpx` with `Authorization: Bearer $GEMINI_API_KEY` header to call the model.
- For `/exec`, validate and run command with `subprocess.run([...], capture_output=True, text=True, timeout=10)`.
- Log every request and response metadata.

## Testing & CI

- Add `tests/test_agent.py` with mock `httpx` responses to ensure `/chat` and `/exec` behave as expected.
- CI: run `python -m pytest` and `flake8` if added.

## UX — interactive terminal usage

1. First-time: `./scripts/termux_install.sh`
2. Start agent: `./scripts/termux_start.sh`
3. In another Termux window: `python agent/cli_client.py --host 127.0.0.1 --port 8080`
4. The CLI supports two modes: `chat:` free text; `exec: ls -la` to run whitelisted commands.

## Operational tips for Termux

- Use `tmux` to keep processes running (Termux sessions may suspend when screen locks). Alternatively use `Termux:Boot` to start at device boot.
- To keep longer-running background processes, consider `termux-wake-lock` (prevents device sleeping while agent runs).

## Appendix — Example .env.example
```
GEMINI_API_URL=https://api.example.com/v1/gemini
GEMINI_API_KEY=
AGENT_PORT=8080
ALLOWED_SHELL_CMDS=ls,cat,pwd,whoami,df,free
LOG_PATH=./agent/logs/agent.log
MAX_RESPONSE_TOKENS=800
```
