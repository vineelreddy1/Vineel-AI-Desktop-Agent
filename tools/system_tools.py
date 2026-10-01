import subprocess
import logging
from computer import windows, screenshots

logger = logging.getLogger("VineelAssistant.SystemTools")

def execute_shell_command(command: str) -> dict:
    """
    Execute a shell command. Requires HIGH risk explicit confirmation.
    """
    logger.warning(f"Executing shell command: {command}")
    try:
        res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        return {
            "status": "SUCCESS" if res.returncode == 0 else "FAILED",
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
            "returncode": res.returncode,
            "message": f"Executed shell command with return code {res.returncode}"
        }
    except Exception as e:
        return {"status": "FAILED", "message": f"Failed shell execution: {str(e)}"}


def shutdown_system() -> dict:
    """
    Initiate Windows shutdown sequence (HIGH risk).
    """
    return execute_shell_command("shutdown /s /t 60")


def reboot_system() -> dict:
    """
    Initiate Windows reboot sequence (HIGH risk).
    """
    return execute_shell_command("shutdown /r /t 60")


TOOLS = {
    # Window Tools
    "list_windows": {
        "name": "list_windows",
        "description": "List titles of all visible open windows.",
        "risk_level": "LOW",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: windows.list_windows()
    },
    "get_active_window": {
        "name": "get_active_window",
        "description": "Get the window title of the active foreground window.",
        "risk_level": "LOW",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: windows.get_active_window()
    },
    "focus_window": {
        "name": "focus_window",
        "description": "Focus/activate a specific window by matching title.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "window_name": {"type": "string", "description": "Title or substring of target window"}
            },
            "required": ["window_name"]
        },
        "func": lambda window_name: windows.focus_window(window_name)
    },
    "minimize_window": {
        "name": "minimize_window",
        "description": "Minimize current active window or specified window.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "window_name": {"type": "string", "description": "Optional title of window to minimize"}
            }
        },
        "func": lambda window_name=None: windows.minimize_window(window_name)
    },
    "maximize_window": {
        "name": "maximize_window",
        "description": "Maximize current active window or specified window.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "window_name": {"type": "string", "description": "Optional title of window to maximize"}
            }
        },
        "func": lambda window_name=None: windows.maximize_window(window_name)
    },
    "close_window": {
        "name": "close_window",
        "description": "Close currently active window or specified window.",
        "risk_level": "MEDIUM",
        "parameters": {
            "type": "object",
            "properties": {
                "window_name": {"type": "string", "description": "Optional title of window to close"}
            }
        },
        "func": lambda window_name=None: windows.close_window(window_name)
    },
    # Screenshot Tools
    "take_screenshot": {
        "name": "take_screenshot",
        "description": "Capture full screen screenshot and save to screenshots folder.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Optional output filename"}
            }
        },
        "func": lambda filename=None: screenshots.take_screenshot(filename)
    },
    "get_screen_size": {
        "name": "get_screen_size",
        "description": "Get current monitor display resolution.",
        "risk_level": "LOW",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: screenshots.get_screen_size()
    },
    # System Tools
    "execute_shell_command": {
        "name": "execute_shell_command",
        "description": "Execute a raw shell command (HIGH RISK - Requires confirmation).",
        "risk_level": "HIGH",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"}
            },
            "required": ["command"]
        },
        "func": lambda command: execute_shell_command(command)
    },
    "shutdown_system": {
        "name": "shutdown_system",
        "description": "Shutdown computer system (HIGH RISK - Requires confirmation).",
        "risk_level": "HIGH",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: shutdown_system()
    },
    "reboot_system": {
        "name": "reboot_system",
        "description": "Reboot computer system (HIGH RISK - Requires confirmation).",
        "risk_level": "HIGH",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: reboot_system()
    }
}
