#!/data/data/com.termux/files/usr/bin/bash

# Exit on any error
set -e

echo "--- Starting xTerminal Agent Installation ---"

# 1. Update Termux packages
echo "[1/5] Updating Termux packages..."
pkg update && pkg upgrade -y

# 2. Install dependencies
echo "[2/5] Installing dependencies (python, git, tmux)..."
pkg install python git tmux -y

# 3. Clone the repository
# Assuming this script is not run from within the repo itself.
# If it is, this step should be skipped by the user.
if [ ! -d "xTerminal" ]; then
    echo "[3/5] Cloning the xTerminal repository..."
    git clone https://github.com/likhoncodes/xTerminal.git
    cd xTerminal
else
    echo "[3/5] Assuming already in xTerminal repository. Skipping clone."
fi

# Change to the agent directory
# This assumes the script is run from the repo root.
if [ ! -d "agent" ]; then
    echo "Error: 'agent' directory not found. Please run this script from the root of the xTerminal repository."
    exit 1
fi

# 4. Set up Python virtual environment
echo "[4/5] Setting up Python virtual environment..."
cd agent
python -m venv .venv
source .venv/bin/activate

# 5. Install Python dependencies
echo "[5/5] Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Final instructions
echo ""
echo "--- Installation Complete! ---"
echo "Next steps:"
echo "1. Create your .env file: cp .env.example .env"
echo "2. Edit the .env file to add your GEMINI_API_KEY: nano .env"
echo "3. Start the agent with: ../scripts/termux_start.sh"
echo "--------------------------------"

# Deactivate venv for the current session if needed, the user will activate it via start script.
deactivate
