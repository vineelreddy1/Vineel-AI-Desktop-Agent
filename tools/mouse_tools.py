from computer import mouse

TOOLS = {
    "move_mouse": {
        "name": "move_mouse",
        "description": "Move mouse cursor to screen coordinates (x, y).",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "Horizontal X coordinate"},
                "y": {"type": "integer", "description": "Vertical Y coordinate"}
            },
            "required": ["x", "y"]
        },
        "func": lambda x, y: mouse.move_mouse(x, y)
    },
    "click": {
        "name": "click",
        "description": "Click mouse button at current position or optional (x, y) coordinates.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "Optional X coordinate"},
                "y": {"type": "integer", "description": "Optional Y coordinate"},
                "button": {"type": "string", "enum": ["left", "right", "middle"], "default": "left"}
            }
        },
        "func": lambda x=None, y=None, button="left": mouse.click(x, y, button)
    },
    "double_click": {
        "name": "double_click",
        "description": "Double click mouse button at current position or optional (x, y) coordinates.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "Optional X coordinate"},
                "y": {"type": "integer", "description": "Optional Y coordinate"}
            }
        },
        "func": lambda x=None, y=None: mouse.double_click(x, y)
    },
    "right_click": {
        "name": "right_click",
        "description": "Right click mouse button at current position or optional (x, y) coordinates.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "Optional X coordinate"},
                "y": {"type": "integer", "description": "Optional Y coordinate"}
            }
        },
        "func": lambda x=None, y=None: mouse.right_click(x, y)
    },
    "scroll": {
        "name": "scroll",
        "description": "Scroll mouse wheel up (positive integer) or down (negative integer).",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "Scroll amount (e.g. 500 for up, -500 for down)"}
            },
            "required": ["amount"]
        },
        "func": lambda amount: mouse.scroll(amount)
    }
}
