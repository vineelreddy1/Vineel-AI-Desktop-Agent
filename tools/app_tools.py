from computer import applications

TOOLS = {
    "open_application": {
        "name": "open_application",
        "description": "Launch a desktop application by name or alias (e.g. 'chrome', 'notepad', 'vs code', 'calculator').",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Name or alias of the application to open"}
            },
            "required": ["app_name"]
        },
        "func": lambda app_name: applications.open_application(app_name)
    },
    "close_application": {
        "name": "close_application",
        "description": "Close/terminate a running desktop application.",
        "risk_level": "MEDIUM",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Name or alias of the application to close"}
            },
            "required": ["app_name"]
        },
        "func": lambda app_name: applications.close_application(app_name)
    },
    "restart_application": {
        "name": "restart_application",
        "description": "Restart a desktop application.",
        "risk_level": "MEDIUM",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Name of application to restart"}
            },
            "required": ["app_name"]
        },
        "func": lambda app_name: applications.restart_application(app_name)
    },
    "is_application_running": {
        "name": "is_application_running",
        "description": "Check if an application process is currently running.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Name of application to check"}
            },
            "required": ["app_name"]
        },
        "func": lambda app_name: {"status": "SUCCESS", "running": applications.is_application_running(app_name)}
    },
    "focus_application": {
        "name": "focus_application",
        "description": "Bring an open application window to foreground.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Name of application to bring into focus"}
            },
            "required": ["app_name"]
        },
        "func": lambda app_name: applications.focus_application(app_name)
    }
}
