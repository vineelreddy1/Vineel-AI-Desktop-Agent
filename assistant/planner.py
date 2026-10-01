import re
import json
import logging
import config
from tools import list_tools, TOOL_REGISTRY

logger = logging.getLogger("VineelAssistant.Planner")

SYSTEM_PROMPT = """You are Vineel Assistant's AI Command Planner.
Your job is to convert natural language desktop commands into a sequence of tool calls.

Available Tools:
{tools_doc}

Rules:
1. Return ONLY a valid JSON array of tool objects. No markdown wrappers, no commentary.
2. Each object must have:
   "tool": string (exact tool name)
   "args": object (key-value parameter dict matching tool arguments)
   "risk": string ("LOW", "MEDIUM", or "HIGH")
3. For multi-step tasks (e.g. "Open Chrome and search YouTube for Java DSA"), output steps in exact execution order.
4. Keep action plans minimal and efficient.
"""


class Planner:
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.model = config.LLM_MODEL
        self.openai_key = config.OPENAI_API_KEY
        self.gemini_key = config.GEMINI_API_KEY

    def _build_tools_doc(self) -> str:
        doc_lines = []
        for name, tool in TOOL_REGISTRY.items():
            doc_lines.append(f"- {name}: {tool['description']} (Risk: {tool['risk_level']}) Params: {tool['parameters']}")
        return "\n".join(doc_lines)

    def plan(self, user_command: str, context: dict = None) -> list:
        logger.info(f"Generating LLM plan for command: '{user_command}' via provider '{self.provider}'")

        if self.provider == "openai" and self.openai_key:
            return self._plan_openai(user_command, context)
        elif self.provider == "gemini" and self.gemini_key:
            return self._plan_gemini(user_command, context)
        else:
            return self._plan_mock(user_command, context)

    def _plan_openai(self, command: str, context: dict) -> list:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            prompt = SYSTEM_PROMPT.format(tools_doc=self._build_tools_doc())

            resp = client.chat.completions.create(
                model=self.model if self.model else "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Command: {command}\nContext: {json.dumps(context or {})}"}
                ],
                temperature=0.0
            )
            raw = resp.choices[0].message.content.strip()
            clean_json = raw.strip("`").replace("json\n", "")
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"OpenAI planning failed: {e}. Falling back to mock planner.")
            return self._plan_mock(command, context)

    def _plan_gemini(self, command: str, context: dict) -> list:
        try:
            from google import genai
            client = genai.Client(api_key=self.gemini_key)
            prompt = SYSTEM_PROMPT.format(tools_doc=self._build_tools_doc())

            candidate_models = [self.model, "gemini-3.8-flash", "gemini-flash-latest"]
            response = None
            last_err = None

            for m in candidate_models:
                if not m:
                    continue
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=f"{prompt}\nUser Command: {command}\nContext: {json.dumps(context or {})}"
                    )
                    if response and response.text:
                        break
                except Exception as err:
                    last_err = err
                    logger.warning(f"Gemini model '{m}' failed: {err}")

            if not response or not response.text:
                raise Exception(f"All Gemini candidate models failed. Last error: {last_err}")

            raw = response.text.strip()
            clean_json = raw.strip("`").replace("json\n", "")
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Gemini planning failed: {e}. Falling back to mock planner.")
            return self._plan_mock(command, context)

    def _plan_mock(self, command: str, context: dict) -> list:
        """
        Intelligent mock planner fallback when LLM API calls fail or are offline.
        Parses common app and search compound phrases.
        """
        cmd_clean = command.strip().lower()

        # Check explicit 4-step YouTube search sequence
        if "chrome" in cmd_clean and "youtube" in cmd_clean and "search" in cmd_clean:
            query = "Java DSA"
            if "search for" in cmd_clean:
                query = cmd_clean.split("search for")[-1].replace("and press enter", "").strip(" .")
            elif "search" in cmd_clean:
                query = cmd_clean.split("search")[-1].replace("and press enter", "").strip(" .")

            return [
                {"tool": "open_application", "args": {"app_name": "chrome"}, "risk": "LOW"},
                {"tool": "open_url", "args": {"url": "https://www.youtube.com"}, "risk": "LOW"},
                {"tool": "search_web", "args": {"query": query, "engine": "youtube"}, "risk": "LOW"},
                {"tool": "press_key", "args": {"key": "enter"}, "risk": "LOW"}
            ]

        # Handle compound "open [app] and search [query]"
        m = re.search(r"(?:open|launch)\s+([a-z0-9\s]+?)\s+(?:and\s+)?search\s+(?:for\s+)?(.+)", cmd_clean)
        if m:
            app_name = m.group(1).strip()
            search_query = m.group(2).strip()
            return [
                {"tool": "open_application", "args": {"app_name": app_name}, "risk": "LOW"},
                {"tool": "search_web", "args": {"query": search_query, "engine": "google"}, "risk": "LOW"}
            ]

        # Handle "search [query]"
        m = re.search(r"search\s+(?:for\s+)?(.+)", cmd_clean)
        if m:
            search_query = m.group(1).strip()
            return [
                {"tool": "search_web", "args": {"query": search_query, "engine": "google"}, "risk": "LOW"}
            ]

        # Extract app name from simple "open [app]" or fallback
        m = re.search(r"(?:open|launch|start)\s+([a-z0-9\s]+)", cmd_clean)
        if m:
            app_name = m.group(1).strip()
            return [{"tool": "open_application", "args": {"app_name": app_name}, "risk": "LOW"}]

        return [{"tool": "open_application", "args": {"app_name": command}, "risk": "LOW"}]
