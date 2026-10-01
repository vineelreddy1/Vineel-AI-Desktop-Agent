from browser import browser_controller

TOOLS = {
    "open_url": {
        "name": "open_url",
        "description": "Open a website URL in the web browser (e.g. 'https://youtube.com').",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL or domain to navigate to"}
            },
            "required": ["url"]
        },
        "func": lambda url: browser_controller.open_url(url)
    },
    "search_web": {
        "name": "search_web",
        "description": "Search Google or YouTube for a query.",
        "risk_level": "LOW",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text"},
                "engine": {"type": "string", "enum": ["google", "youtube"], "default": "google"}
            },
            "required": ["query"]
        },
        "func": lambda query, engine="google": browser_controller.search_web(query, engine)
    },
    "go_back": {
        "name": "go_back",
        "description": "Navigate back in browser history.",
        "risk_level": "LOW",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: browser_controller.go_back()
    },
    "go_forward": {
        "name": "go_forward",
        "description": "Navigate forward in browser history.",
        "risk_level": "LOW",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: browser_controller.go_forward()
    },
    "refresh_page": {
        "name": "refresh_page",
        "description": "Reload current browser page.",
        "risk_level": "LOW",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: browser_controller.refresh_page()
    },
    "new_tab": {
        "name": "new_tab",
        "description": "Open a new blank browser tab.",
        "risk_level": "LOW",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: browser_controller.new_tab()
    },
    "close_tab": {
        "name": "close_tab",
        "description": "Close current browser tab.",
        "risk_level": "LOW",
        "parameters": {"type": "object", "properties": {}},
        "func": lambda: browser_controller.close_tab()
    }
}
