# xTerminal - Your AI Assistant for the Command Line

xTerminal is a project that provides a self-hosted, Gemini-powered AI agent designed to run on any machine, with a special focus on Termux for Android devices. It gives you an intelligent command-line assistant that can answer questions and safely execute whitelisted shell commands.

![xTerminal Concept](https://i.imgur.com/your-image-url.png) _(Note: Replace with an actual screenshot or diagram)_

## Features

- **Gemini-Powered Chat**: Interact with a powerful language model directly from your terminal.
- **Safe Command Execution**: The agent can run shell commands, but only those explicitly permitted in your configuration. All executed commands are logged.
- **Termux-Ready**: Designed to be lightweight and efficient, making it perfect for running on Android devices via Termux.
- **Self-Hosted**: You control the agent. It runs on your local device or any server you choose.
- **Easy to Set Up**: Includes simple installation and startup scripts for a quick start.
- **Extensible**: Built with FastAPI, making it easy to add new capabilities.

## Getting Started

These instructions are tailored for setting up the xTerminal agent on a new Termux instance.

### Prerequisites

- Termux (latest version from F-Droid)
- `git` installed in Termux (`pkg install git`)

### Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/likhoncodes/xTerminal.git
    cd xTerminal
    ```

2.  **Run the Install Script**:
    This script will install dependencies like Python and `tmux`, set up a virtual environment, and install the required Python packages.
    ```bash
    chmod +x ./scripts/termux_install.sh
    ./scripts/termux_install.sh
    ```

3.  **Configure Your API Key**:
    The installer will create an `.env` file in the `agent/` directory. You must edit this file to add your Gemini API key.
    ```bash
    nano agent/.env
    ```
    Find the line `GEMINI_API_KEY=` and add your key.

### Running the Agent

The agent is designed to run as a background service using `tmux`.

1.  **Start the Agent**:
    ```bash
    chmod +x ./scripts/termux_start.sh
    ./scripts/termux_start.sh
    ```
    This will start the agent in a detached `tmux` session named `xterminal`.

2.  **Check the Agent's Status**:
    You can "attach" to the `tmux` session to see the agent's log output:
    ```bash
    tmux attach -t xterminal
    ```
    To detach (and keep it running in the background), press `Ctrl+b` then `d`.

3.  **Stopping the Agent**:
    ```bash
    tmux kill-session -t xterminal
    ```

## Using the CLI Client

Once the agent is running, open a **new** Termux session to use the interactive client.

1.  **Launch the Client**:
    ```bash
    python agent/cli_client.py
    ```

2.  **Interact with the Agent**:
    The client supports two main commands:
    - `chat: <your message>`: Send a message to the Gemini model.
    - `exec: <command>`: Execute a whitelisted shell command.

    **Example:**
    ```
    xTerminal> chat: what is the capital of France?

    🤖 Agent Response:
    The capital of France is Paris.
    --------------------
    xTerminal> exec: ls -l agent/

    --- STDOUT ---
    -rw-r--r-- 1 u0_a182 u0_a182 4813 Dec 19 14:30 app.py
    -rw-r--r-- 1 u0_a182 u0_a182 1782 Dec 19 14:30 cli_client.py
    -rw-r--r-- 1 u0_a182 u0_a182  159 Dec 19 14:30 .env.example
    -rw-r--r-- 1 u0_a182 u0_a182  418 Dec 19 14:30 README_AGENT.md
    -rw-r--r-- 1 u0_a182 u0_a182  148 Dec 19 14:30 requirements.txt
    ```

3.  **Get Help**:
    Type `help` in the client to see the list of commands.

## Project Structure

```
.
├── agent/                # The core FastAPI agent and CLI client
│   ├── app.py            # FastAPI server
│   ├── cli_client.py     # Interactive CLI
│   ├── .env.example      # Environment variable template
│   └── requirements.txt  # Python dependencies
├── scripts/              # Installation and startup scripts
│   ├── termux_install.sh
│   └── termux_start.sh
├── tests/                # Pytest test suite
└── termux/               # Notes for advanced Termux usage
```
