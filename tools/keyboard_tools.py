from computer import keyboard

TOOLS = {
    "type_text": {
        "name": "type_text",
        "description": "Type text using keyboard simulation into the currently focused window.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The exact string content to type"}
            },
            "required": ["text"]
        },
        "func": lambda text: keyboard.type_text(text)
    },
    "press_key": {
        "name": "press_key",
        "description": "Press a single keyboard key (e.g. 'enter', 'escape', 'space', 'tab', 'backspace').",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key name to press"}
            },
            "required": ["key"]
        },
        "func": lambda key: keyboard.press_key(key)
    },
    "hotkey": {
        "name": "hotkey",
        "description": "Press a sequence or combination of keys together (e.g. ['ctrl', 'l'], ['alt', 'tab'], ['ctrl', 'c']).",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of key names to press in hotkey combination"
                }
            },
            "required": ["keys"]
        },
        "func": lambda keys: keyboard.hotkey(keys)
    }
}
