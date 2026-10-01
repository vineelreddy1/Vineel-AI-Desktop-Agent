import os
import time
import logging
from pathlib import Path
import pyautogui
from PIL import Image
import config

logger = logging.getLogger("VineelAssistant.Screenshots")

pyautogui.FAILSAFE = False


def get_screen_size() -> dict:
    """
    Get current screen resolution (width, height).
    """
    try:
        width, height = pyautogui.size()
        return {"status": "SUCCESS", "width": width, "height": height, "message": f"Screen resolution: {width}x{height}"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Failed to get screen size: {str(e)}"}


def take_screenshot(filename: str = None) -> dict:
    """
    Capture a screenshot of the entire primary display.
    """
    try:
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            
        save_path = config.SCREENSHOTS_DIR / filename
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        logger.info(f"Screenshot saved to: {save_path}")
        
        return {
            "status": "SUCCESS",
            "path": str(save_path),
            "filename": filename,
            "size": screenshot.size,
            "message": f"Screenshot saved to {save_path}"
        }
    except Exception as e:
        error_msg = f"Failed to capture screenshot: {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


class ScreenAnalyzer:
    """
    Modular interface for future Vision Language Model (VLM) screen analysis.
    Can be extended with GPT-4 Vision, Claude 3.5 Sonnet Vision, or local models (e.g. Qwen2-VL, Moondream).
    """
    def __init__(self, provider: str = "mock"):
        self.provider = provider

    def analyze_screen(self, query: str, screenshot_path: str = None) -> dict:
        """
        Analyze screenshot using query (e.g. 'Find YouTube search box coordinates').
        Returns target coordinates (x, y) or analysis text.
        """
        if not screenshot_path:
            shot_res = take_screenshot()
            if shot_res["status"] != "SUCCESS":
                return shot_res
            screenshot_path = shot_res["path"]

        logger.info(f"Analyzing screen with query: '{query}' via provider '{self.provider}'")

        if self.provider == "mock":
            # Mock screen analyzer response for V1 architecture testing
            width, height = pyautogui.size()
            return {
                "status": "SUCCESS",
                "query": query,
                "analysis": f"Mock analysis for '{query}' on screen size {width}x{height}",
                "suggested_target": {"x": width // 2, "y": height // 2},
                "confidence": 0.95
            }
        else:
            return {"status": "FAILED", "message": f"Vision provider '{self.provider}' not implemented yet."}
