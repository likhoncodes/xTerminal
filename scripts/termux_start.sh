#!/data/data/com.termux/files/usr/bin/bash

# Exit on any error
set -e

# Navigate to the agent directory from the script's location
SCRIPT_DIR=$(dirname "$0")
REPO_ROOT=$(realpath "$SCRIPT_DIR/..")
AGENT_DIR="$REPO_ROOT/agent"

cd "$AGENT_DIR"

echo "--- Starting xTerminal Agent ---"

# 1. Check for .env file
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please run the install script and configure it first."
    exit 1
fi

# 2. Activate virtual environment
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run the install script first."
    exit 1
fi
echo "[1/3] Activating virtual environment..."
source .venv/bin/activate

# 3. Export environment variables
echo "[2/3] Exporting environment variables from .env file..."
export $(grep -v '^#' .env | xargs)

# Check if required variables are set
if [ -z "$GEMINI_API_KEY" ] || [ -z "$AGENT_PORT" ]; then
    echo "Error: GEMINI_API_KEY or AGENT_PORT is not set in the .env file."
    exit 1
fi

# 4. Start the agent with tmux
SESSION_NAME="xterminal"
echo "[3/3] Starting agent in tmux session '$SESSION_NAME'..."

# Check if session already exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
    # Create new detached session
    tmux new-session -d -s $SESSION_NAME "uvicorn app:app --host 0.0.0.0 --port ${AGENT_PORT} --log-level info"
    echo "Agent started successfully in a new tmux session."
    echo "Attach to session with: tmux attach -t $SESSION_NAME"
    echo "Stop the agent with: tmux kill-session -t $SESSION_NAME"
else
    echo "A tmux session named '$SESSION_NAME' is already running."
    echo "Please stop it first if you want to restart the agent: tmux kill-session -t $SESSION_NAME"
fi

echo "--------------------------------"
