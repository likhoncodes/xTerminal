# xTerminal Agent Quick Start

This directory contains the FastAPI agent and the CLI client.

## First-Time Setup

1.  Ensure you are in the root of the `xTerminal` repository.
2.  Run the installation script:
    ```bash
    ./scripts/termux_install.sh
    ```
3.  This will create a virtual environment, install dependencies, and set up your `.env` file.
4.  Edit `agent/.env` to add your `GEMINI_API_KEY`.

## Running the Agent

1.  Start the agent using the start script:
    ```bash
    ./scripts/termux_start.sh
    ```
2.  This will launch the agent in a background `tmux` session.

## Using the CLI

1.  In a new terminal window, run the client:
    ```bash
    python agent/cli_client.py
    ```
2.  You can now interact with the agent. Type `help` for commands.
