import time
import logging
import pyautogui

logger = logging.getLogger("VineelAssistant.Keyboard")

# PyAutoGUI safety settings
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

KEY_MAPPINGS = {
    "control": "ctrl",
    "ctl": "ctrl",
    "enter": "enter",
    "return": "enter",
    "esc": "escape",
    "escape": "escape",
    "space": "space",
    "spacebar": "space",
    "tab": "tab",
    "backspace": "backspace",
    "delete": "delete",
    "del": "delete",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "windows": "win",
    "win": "win",
    "cmd": "win",
    "alt": "alt",
    "shift": "shift",
    "capslock": "capslock"
}


def normalize_key(key: str) -> str:
    k = key.strip().lower()
    return KEY_MAPPINGS.get(k, k)


def type_text(text: str, interval: float = 0.01) -> dict:
    """
    Type out text via PyAutoGUI.
    """
    try:
        logger.info(f"Typing text: {text}")
        pyautogui.write(text, interval=interval)
        return {"status": "SUCCESS", "message": f"Typed: '{text}'"}
    except Exception as e:
        error_msg = f"Failed to type text: {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def press_key(key: str) -> dict:
    """
    Press a single key.
    """
    try:
        norm_key = normalize_key(key)
        logger.info(f"Pressing key: {norm_key}")
        pyautogui.press(norm_key)
        return {"status": "SUCCESS", "message": f"Pressed key: '{norm_key}'"}
    except Exception as e:
        error_msg = f"Failed to press key '{key}': {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def hotkey(keys: list) -> dict:
    """
    Execute a key combination (e.g. ['ctrl', 'c'], ['alt', 'tab']).
    """
    try:
        norm_keys = [normalize_key(str(k)) for k in keys]
        logger.info(f"Executing hotkey combination: {norm_keys}")
        pyautogui.hotkey(*norm_keys)
        return {"status": "SUCCESS", "message": f"Executed hotkey: {' + '.join(norm_keys)}"}
    except Exception as e:
        error_msg = f"Failed to execute hotkey {keys}: {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}
