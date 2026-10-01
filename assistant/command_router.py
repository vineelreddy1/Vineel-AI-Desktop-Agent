import re
import logging

logger = logging.getLogger("VineelAssistant.CommandRouter")

# Conversational filler prefixes to strip
FILLER_PREFIXES = [
    r"^can\s+(?:you|u)\s+(?:please\s+)?",
    r"^could\s+(?:you|u)\s+(?:please\s+)?",
    r"^would\s+(?:you|u)\s+(?:mind\s+)?(?:please\s+)?",
    r"^will\s+(?:you|u)\s+(?:please\s+)?",
    r"^please\s+",
    r"^pls\s+",
    r"^i\s+want\s+to\s+",
    r"^hey\s+vineel\s*,?\s*",
    r"^vineel\s*,?\s*"
]


def sanitize_command(command: str) -> str:
    """
    Remove conversational filler prefixes and trailing punctuation.
    """
    text = command.strip()
    for pattern in FILLER_PREFIXES:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
    text = text.rstrip(" .?!,")
    return text


class CommandRouter:
    """
    Fast offline local rule-based command router for natural language commands.
    """
    def __init__(self):
        pass

    def route_single(self, command: str) -> dict | None:
        cmd = sanitize_command(command).lower()
        if not cmd:
            return None

        # 1. Open / Launch / Start Application or Site
        m = re.match(r"^(?:open|launch|start|run)\s+(.+)$", cmd)
        if m:
            target = m.group(1).strip()
            # Special check for browser site names
            if target in ["youtube", "google", "github", "reddit", "twitter", "wikipedia"] or "." in target or target.startswith("http"):
                url = target if target.startswith("http") or "." in target else f"https://www.{target}.com"
                return {
                    "matched": True,
                    "plan": [{"tool": "open_url", "args": {"url": url}, "risk": "LOW"}],
                    "response_text": f"Opening {target} in browser."
                }
            return {
                "matched": True,
                "plan": [{"tool": "open_application", "args": {"app_name": target}, "risk": "LOW"}],
                "response_text": f"Opening {target}."
            }

        # 2. Close Application / Window / Tab
        m = re.match(r"^(?:close|quit|exit|kill)\s+(.+)$", cmd)
        if m:
            target = m.group(1).strip()
            if target in ["tab", "this tab", "current tab"]:
                return {
                    "matched": True,
                    "plan": [{"tool": "close_tab", "args": {}, "risk": "LOW"}],
                    "response_text": "Closing tab."
                }
            if target in ["window", "this window", "current window"]:
                return {
                    "matched": True,
                    "plan": [{"tool": "close_window", "args": {}, "risk": "MEDIUM"}],
                    "response_text": "Closing window."
                }
            return {
                "matched": True,
                "plan": [{"tool": "close_application", "args": {"app_name": target}, "risk": "MEDIUM"}],
                "response_text": f"Closing {target}."
            }

        # 3. Switch to / Focus Application
        m = re.match(r"^(?:switch to|focus|go to window)\s+(.+)$", cmd)
        if m:
            target = m.group(1).strip()
            return {
                "matched": True,
                "plan": [{"tool": "focus_application", "args": {"app_name": target}, "risk": "LOW"}],
                "response_text": f"Switching to {target}."
            }

        # 4. Type text / write text
        m = re.match(r"^(?:type|write|input)\s+(.+)$", cmd)
        if m:
            raw_clean = sanitize_command(command)
            text_to_type = raw_clean[len(raw_clean.split()[0]):].strip()
            return {
                "matched": True,
                "plan": [{"tool": "type_text", "args": {"text": text_to_type}, "risk": "LOW"}],
                "response_text": f"Typing '{text_to_type}'."
            }

        # 5. Hotkeys & Short Controls
        if cmd in ["copy this", "copy"]:
            return {"matched": True, "plan": [{"tool": "hotkey", "args": {"keys": ["ctrl", "c"]}, "risk": "LOW"}], "response_text": "Copied."}
        if cmd in ["paste it", "paste"]:
            return {"matched": True, "plan": [{"tool": "hotkey", "args": {"keys": ["ctrl", "v"]}, "risk": "LOW"}], "response_text": "Pasted."}
        if cmd in ["go back", "back"]:
            return {"matched": True, "plan": [{"tool": "go_back", "args": {}, "risk": "LOW"}], "response_text": "Going back."}
        if cmd in ["refresh the page", "refresh page", "refresh", "reload"]:
            return {"matched": True, "plan": [{"tool": "refresh_page", "args": {}, "risk": "LOW"}], "response_text": "Refreshing page."}
        if cmd in ["open a new tab", "open new tab", "new tab"]:
            return {"matched": True, "plan": [{"tool": "new_tab", "args": {}, "risk": "LOW"}], "response_text": "Opening new tab."}
        if cmd in ["close this tab", "close tab"]:
            return {"matched": True, "plan": [{"tool": "close_tab", "args": {}, "risk": "LOW"}], "response_text": "Closing tab."}
        if cmd in ["take screenshot", "capture screen", "screenshot"]:
            return {"matched": True, "plan": [{"tool": "take_screenshot", "args": {}, "risk": "LOW"}], "response_text": "Taking screenshot."}

        # 6. Press key / Press hotkey
        m = re.match(r"^(?:press|hit)\s+(.+)$", cmd)
        if m:
            key_expr = m.group(1).strip()
            parts = key_expr.split()
            if len(parts) > 1:
                return {
                    "matched": True,
                    "plan": [{"tool": "hotkey", "args": {"keys": parts}, "risk": "LOW"}],
                    "response_text": f"Pressing {' + '.join(parts)}."
                }
            else:
                return {
                    "matched": True,
                    "plan": [{"tool": "press_key", "args": {"key": parts[0]}, "risk": "LOW"}],
                    "response_text": f"Pressing {parts[0]}."
                }

        # 7. Go to URL / Web Navigation
        m = re.match(r"^(?:go to|navigate to|open website)\s+(.+)$", cmd)
        if m:
            dest = m.group(1).strip()
            url = dest if dest.startswith("http") or "." in dest else f"https://www.{dest}.com"
            return {
                "matched": True,
                "plan": [{"tool": "open_url", "args": {"url": url}, "risk": "LOW"}],
                "response_text": f"Navigating to {dest}."
            }

        # 8. Web Search (Google / YouTube / General)
        raw_sanitized = sanitize_command(command)
        m = re.match(r"^search\s+(youtube|google)?\s*(?:for)?\s*(.*)$", raw_sanitized, flags=re.IGNORECASE)
        if m:
            engine = (m.group(1) or "google").lower()
            query = m.group(2).strip()
            if not query and engine == "youtube":
                return {
                    "matched": True,
                    "plan": [{"tool": "open_url", "args": {"url": "https://www.youtube.com"}, "risk": "LOW"}],
                    "response_text": "Opening YouTube."
                }
            if query:
                return {
                    "matched": True,
                    "plan": [{"tool": "search_web", "args": {"query": query, "engine": engine}, "risk": "LOW"}],
                    "response_text": f"Searching {engine} for {query}."
                }

        return None

    def route(self, command: str) -> dict | None:
        """
        Routes single or multi-step conjunction commands.
        """
        clean_command = sanitize_command(command)
        delimiters = r"\s+and then\s+|\s+then\s+|\s+and\s+|,\s*"
        parts = [p.strip() for p in re.split(delimiters, clean_command, flags=re.IGNORECASE) if p.strip()]

        if len(parts) <= 1:
            return self.route_single(clean_command)

        combined_plan = []
        response_parts = []
        for part in parts:
            res = self.route_single(part)
            if res and res.get("matched"):
                combined_plan.extend(res["plan"])
                response_parts.append(res["response_text"])
            else:
                return None

        return {
            "matched": True,
            "plan": combined_plan,
            "response_text": " ".join(response_parts)
        }
