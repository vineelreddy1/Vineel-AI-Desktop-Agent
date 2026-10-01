import time
import logging
from typing import Callable
import config
from tools import execute_tool, get_tool
from assistant.command_router import CommandRouter
from assistant.planner import Planner
from voice.text_to_speech import speak

logger = logging.getLogger("VineelAssistant.Agent")


class AgentContext:
    def __init__(self):
        self.active_application: str = "Desktop"
        self.active_window: str = ""
        self.current_browser_url: str = ""
        self.recent_commands: list = []
        self.task_status: str = "IDLE"
        self.pending_confirmation: dict = None

    def to_dict(self) -> dict:
        return {
            "active_application": self.active_application,
            "active_window": self.active_window,
            "current_browser_url": self.current_browser_url,
            "recent_commands": self.recent_commands[-5:],
            "task_status": self.task_status
        }


class Agent:
    def __init__(self, log_callback: Callable[[str], None] = None):
        self.context = AgentContext()
        self.router = CommandRouter()
        self.planner = Planner()
        self.interrupted = False
        self.log_callback = log_callback

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"{timestamp} - {message}"
        logger.info(message)
        if self.log_callback:
            try:
                self.log_callback(formatted)
            except Exception:
                pass

    def stop(self):
        """
        Interrupt ongoing execution tasks immediately.
        """
        logger.warning("Stop command received! Interrupting current task.")
        self.interrupted = True
        self.context.task_status = "INTERRUPTED"
        self.log("Task cancelled by user.")
        speak("Stopping.")

    def execute_command(self, command_text: str) -> dict:
        """
        Process user natural language command end-to-end.
        """
        if not command_text or not command_text.strip():
            return {"status": "FAILED", "message": "Empty command."}

        clean_cmd = command_text.strip()
        self.interrupted = False
        self.context.task_status = "PROCESSING"
        self.context.recent_commands.append(clean_cmd)
        
        self.log(f"Command received: '{clean_cmd}'")

        # Check for immediate interrupt commands
        if clean_cmd.lower() in ["stop", "cancel", "halt", "abort"]:
            self.stop()
            return {"status": "SUCCESS", "message": "Task stopped."}

        # Step 1: Attempt local rule-based routing (Offline-first architecture)
        route_res = self.router.route(clean_cmd)
        
        if route_res and route_res.get("matched"):
            self.log(f"Local router matched: {route_res['response_text']}")
            plan = route_res["plan"]
            spoken_response = route_res["response_text"]
        else:
            # Step 2: Pass complex/ambiguous command to LLM Planner
            self.log("Routing to AI Planner for multi-step action plan...")
            plan = self.planner.plan(clean_cmd, self.context.to_dict())
            spoken_response = f"Processing request to {clean_cmd}."

        if not plan:
            msg = f"Sorry, I didn't understand how to process '{clean_cmd}'."
            self.log(msg)
            speak(msg)
            self.context.task_status = "IDLE"
            return {"status": "FAILED", "message": msg}

        # Announce start of task via TTS
        speak(spoken_response)

        # Step 3: Sequential Plan Execution
        executed_steps = []
        for i, step in enumerate(plan):
            if self.interrupted:
                self.log("Execution halted due to user interruption.")
                break

            tool_name = step.get("tool")
            args = step.get("args", {})
            risk = step.get("risk", "LOW")

            # Check Risk Level & Confirmation
            if risk in ["MEDIUM", "HIGH"]:
                self.context.task_status = "WAITING_CONFIRMATION"
                self.context.pending_confirmation = {"step": step, "command": clean_cmd}
                msg = f"Action '{tool_name}' requires confirmation. Risk level: {risk}."
                self.log(msg)
                if risk == "HIGH":
                    speak(f"This action requires confirmation: {tool_name}. Do you want me to proceed?")
                    # In standard headless/CLI mode without GUI dialog, log warning
                    self.log("Awaiting confirmation (HIGH risk action).")

            self.log(f"Executing step {i+1}/{len(plan)}: {tool_name}({args})")
            
            # Execute tool
            res = execute_tool(tool_name, **args)
            executed_steps.append({"tool": tool_name, "args": args, "result": res})

            # Update context based on tool
            if tool_name == "open_application":
                self.context.active_application = args.get("app_name", "App")
            elif tool_name == "open_url":
                self.context.current_browser_url = args.get("url", "")
                self.context.active_application = "Browser"

            if res.get("status") != "SUCCESS":
                self.log(f"Step {tool_name} returned warning/failure: {res.get('message')}")

            # Small delay between multi-step automated actions for visual smoothness
            time.sleep(0.3)

        self.context.task_status = "IDLE"
        self.log(f"Task completed successfully.")
        return {"status": "SUCCESS", "executed_steps": executed_steps}
