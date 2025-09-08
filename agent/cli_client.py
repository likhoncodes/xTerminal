import argparse
import httpx
import sys

def print_help():
    """Prints the help message."""
    print("\n--- xTerminal CLI Client ---")
    print("Available commands:")
    print("  chat: <your message>  - Send a message to the Gemini agent.")
    print("  exec: <command>       - Execute a whitelisted shell command.")
    print("  help                 - Show this help message.")
    print("  exit                 - Exit the client.")
    print("--------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="CLI client for the xTerminal agent.")
    parser.add_argument("--host", default="127.0.0.1", help="Host of the agent.")
    parser.add_argument("--port", type=int, default=8080, help="Port of the agent.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose error reporting.")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    # Check agent health on startup
    try:
        with httpx.Client() as client:
            response = client.get(f"{base_url}/health")
            response.raise_for_status()
        print("Successfully connected to xTerminal agent. Type 'help' for commands.")
    except httpx.RequestError as e:
        print(f"Error: Could not connect to the agent at {base_url}.")
        if args.verbose:
            print(f"Details: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("xTerminal> ").strip()
            if not user_input:
                continue

            if user_input.lower() == 'exit':
                print("Exiting client.")
                break

            if user_input.lower() == 'help':
                print_help()
                continue

            with httpx.Client(timeout=45.0) as client:
                if user_input.lower().startswith("exec:"):
                    cmd_str = user_input[5:].strip()
                    if not cmd_str:
                        print("Error: 'exec' command requires an argument.")
                        continue

                    response = client.post(f"{base_url}/exec", json={"cmd": cmd_str})
                    response.raise_for_status()

                    data = response.json()
                    if data.get("stdout"):
                        print("--- STDOUT ---")
                        print(data["stdout"].strip())
                    if data.get("stderr"):
                        print("--- STDERR ---")
                        print(data["stderr"].strip())
                    if not data.get("stdout") and not data.get("stderr"):
                        print("(Command produced no output)")

                elif user_input.lower().startswith("chat:"):
                    msg_str = user_input[5:].strip()
                    if not msg_str:
                        print("Error: 'chat' command requires an argument.")
                        continue

                    response = client.post(f"{base_url}/chat", json={"input": msg_str})
                    response.raise_for_status()

                    data = response.json()
                    print("\n🤖 Agent Response:")
                    print(data.get("response", "(No response from agent)"))
                    print("-" * 20)

                else:
                    print("Unknown command. Type 'help' to see available commands.")

        except httpx.HTTPStatusError as e:
            print(f"\nError: Received status {e.response.status_code} from agent.")
            if args.verbose:
                try:
                    # Try to print the detail from the JSON response
                    error_detail = e.response.json().get("detail", e.response.text)
                    print(f"Details: {error_detail}")
                except:
                    print(f"Details: {e.response.text}")
        except httpx.RequestError as e:
            print(f"\nError: Could not communicate with the agent.")
            if args.verbose:
                print(f"Details: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting client.")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred.")
            if args.verbose:
                print(f"Details: {e}")


if __name__ == "__main__":
    main()
