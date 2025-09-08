# Notes for Running the xTerminal Agent on Termux

This document provides tips for ensuring the agent runs reliably and persistently in the Termux environment on Android.

## Keeping the Agent Running

Android's battery optimization can be aggressive and may terminate background processes, including Termux sessions. To ensure the agent stays online, consider the following methods.

### 1. Using `tmux` (Recommended)

The provided `termux_start.sh` script uses `tmux` to run the agent in a background session. This is the primary recommended method.

- **To start:** `./scripts/termux_start.sh`
- **To view the agent's output:** `tmux attach -t xterminal`
- **To detach from the session:** Press `Ctrl+b` then `d`
- **To stop the agent:** `tmux kill-session -t xterminal`

Even with `tmux`, Termux itself might be killed by the OS. To prevent this, you need a wake lock.

### 2. Using `termux-wake-lock`

The `termux-wake-lock` command prevents the device from entering deep sleep, which helps keep Termux and its child processes (like the agent) alive.

You can run this in a separate Termux session while the agent is active.

```bash
# Run this in another terminal after starting the agent
termux-wake-lock
```

You can also add this to the `termux_start.sh` script, but it's often better to manage it manually so you can turn it off easily without stopping the agent.

### 3. Using `Termux:Boot` (Advanced)

For users who want the agent to start automatically when the device boots up, the `Termux:Boot` add-on is a powerful option.

1.  Install the `Termux:Boot` app from F-Droid.
2.  Create a `~/.termux/boot/` directory.
3.  Create a script inside that directory (e.g., `~/.termux/boot/start-xterminal-agent`) with the following content:

    ```bash
    #!/data/data/com.termux/files/usr/bin/sh
    # This script will run on device boot

    # Absolute path to the start script
    /data/data/com.termux/files/home/xTerminal/scripts/termux_start.sh
    ```

This will automatically launch the agent every time you restart your Android device. Make sure the path to the script is correct.
