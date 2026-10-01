import logging
from tools import app_tools, keyboard_tools, mouse_tools, browser_tools, system_tools

logger = logging.getLogger("VineelAssistant.Tools")

TOOL_REGISTRY = {}

# Register all imported tools
for module in [app_tools, keyboard_tools, mouse_tools, browser_tools, system_tools]:
    if hasattr(module, "TOOLS"):
        TOOL_REGISTRY.update(module.TOOLS)


def get_tool(tool_name: str) -> dict:
    return TOOL_REGISTRY.get(tool_name)


def list_tools() -> list:
    return list(TOOL_REGISTRY.values())


def execute_tool(tool_name: str, **kwargs) -> dict:
    """
    Execute tool safely with argument validation.
    """
    tool_def = get_tool(tool_name)
    if not tool_def:
        msg = f"Tool '{tool_name}' not found in registry."
        logger.error(f"[TOOL] [NAME: {tool_name}] [STATUS: FAILED] Reason: {msg}")
        return {"status": "FAILED", "message": msg}

    logger.info(f"[TOOL] [NAME: {tool_name}] [ARGS: {kwargs}] [STATUS: EXECUTING]")
    try:
        func = tool_def["func"]
        result = func(**kwargs)
        status = result.get("status", "SUCCESS")
        logger.info(f"[TOOL] [NAME: {tool_name}] [ARGS: {kwargs}] [STATUS: {status}]")
        return result
    except Exception as e:
        error_msg = f"Exception executing tool '{tool_name}': {str(e)}"
        logger.error(f"[TOOL] [NAME: {tool_name}] [ARGS: {kwargs}] [STATUS: FAILED] Error: {error_msg}")
        return {"status": "FAILED", "message": error_msg}


def get_llm_tools_schema() -> list:
    """
    Format tools for LLM tool calling (OpenAI format compatible).
    """
    schemas = []
    for name, tool in TOOL_REGISTRY.items():
        schemas.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
        })
    return schemas
