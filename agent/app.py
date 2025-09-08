import os
import logging
import subprocess
from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

GEMINI_API_URL = os.getenv("GEMINI_API_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AGENT_PORT = int(os.getenv("AGENT_PORT", 8080))
ALLOWED_SHELL_CMDS_STR = os.getenv("ALLOWED_SHELL_CMDS", "ls,cat,pwd")
ALLOWED_SHELL_CMDS = [cmd.strip() for cmd in ALLOWED_SHELL_CMDS_STR.split(',')]
LOG_PATH = os.getenv("LOG_PATH", "./agent/logs/agent.log")
MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", 800))

# --- Logging Setup ---
log_dir = os.path.dirname(LOG_PATH)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI(
    title="xTerminal Agent",
    description="A Gemini-powered agent for Termux.",
)

# --- Rate Limiting (Simple In-Memory) ---
# A real implementation would use Redis or a more robust solution.
RATE_LIMIT_MAX_CALLS = 10
RATE_LIMIT_PERIOD_SECONDS = 60
request_counts = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # In a test environment, client might be None.
    client_ip = request.client.host if request.client else "testclient"
    now = datetime.now()

    if client_ip not in request_counts:
        request_counts[client_ip] = []

    # Filter out requests older than the period
    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if (now - t).total_seconds() < RATE_LIMIT_PERIOD_SECONDS
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT_MAX_CALLS:
        # Returning a direct response is more robust for middleware and test clients.
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests"}
        )

    request_counts[client_ip].append(now)
    response = await call_next(request)
    return response


# --- Pydantic Models ---
class ChatInput(BaseModel):
    input: str

class ChatResponse(BaseModel):
    response: str

class ExecInput(BaseModel):
    cmd: str

class ExecResponse(BaseModel):
    stdout: str
    stderr: str
    returncode: int

class HealthResponse(BaseModel):
    status: str = "ok"

# --- API Endpoints ---
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the agent is running."""
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_gemini(payload: ChatInput):
    """Forward a user's input to the Gemini API and get a response."""
    if not GEMINI_API_URL or not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API URL or Key is not configured.")

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }

    # This is a simplified payload for gemini-pro.
    # Real-world usage might require more complex structures.
    json_payload = {
        "contents": [{
            "parts": [{"text": payload.input}]
        }],
        "generationConfig": {
            "maxOutputTokens": MAX_RESPONSE_TOKENS,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GEMINI_API_URL, headers=headers, json=json_payload)
            response.raise_for_status()

            data = response.json()
            # The response structure for Gemini API can be complex.
            # This navigates to the typical location of the text response.
            gemini_response = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

            return {"response": gemini_response}

    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API request failed: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Gemini API error: {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during chat: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")


@app.post("/exec", response_model=ExecResponse)
async def execute_command(payload: ExecInput):
    """Execute a whitelisted shell command."""
    command_parts = payload.cmd.split()
    command_name = command_parts[0]

    if command_name not in ALLOWED_SHELL_CMDS:
        logger.warning(f"Attempt to execute disallowed command: {command_name}")
        raise HTTPException(status_code=403, detail=f"Command '{command_name}' is not allowed.")

    try:
        process = subprocess.run(
            command_parts,
            capture_output=True,
            text=True,
            timeout=15
        )

        stdout = process.stdout
        stderr = process.stderr
        returncode = process.returncode

        # Audit Log
        log_message = f"user='local' cmd='{payload.cmd}' returncode={returncode}"
        logger.info(log_message)

        return {"stdout": stdout, "stderr": stderr, "returncode": returncode}

    except FileNotFoundError:
        logger.error(f"Command not found: {command_name}")
        raise HTTPException(status_code=404, detail=f"Command not found: {command_name}")
    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out: {payload.cmd}")
        raise HTTPException(status_code=408, detail="Command execution timed out.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during command execution: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during command execution.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
