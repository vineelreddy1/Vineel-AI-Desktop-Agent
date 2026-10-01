import logging
import pyautogui

logger = logging.getLogger("VineelAssistant.Mouse")

pyautogui.FAILSAFE = False

def move_mouse(x: int, y: int, duration: float = 0.2) -> dict:
    """
    Move mouse cursor to (x, y).
    """
    try:
        logger.info(f"Moving mouse to ({x}, {y})")
        pyautogui.moveTo(x, y, duration=duration)
        return {"status": "SUCCESS", "message": f"Moved mouse to ({x}, {y})"}
    except Exception as e:
        error_msg = f"Failed to move mouse to ({x}, {y}): {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def click(x: int = None, y: int = None, button: str = "left") -> dict:
    """
    Click at specified position (x, y) or current position if None.
    """
    try:
        if x is not None and y is not None:
            logger.info(f"Clicking mouse at ({x}, {y}) with button {button}")
            pyautogui.click(x=x, y=y, button=button)
            return {"status": "SUCCESS", "message": f"Clicked {button} at ({x}, {y})"}
        else:
            logger.info(f"Clicking mouse at current position with button {button}")
            pyautogui.click(button=button)
            return {"status": "SUCCESS", "message": f"Clicked {button} at current position"}
    except Exception as e:
        error_msg = f"Failed mouse click: {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def double_click(x: int = None, y: int = None) -> dict:
    """
    Double click mouse.
    """
    try:
        if x is not None and y is not None:
            pyautogui.doubleClick(x=x, y=y)
            return {"status": "SUCCESS", "message": f"Double clicked at ({x}, {y})"}
        else:
            pyautogui.doubleClick()
            return {"status": "SUCCESS", "message": f"Double clicked at current position"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Failed double click: {str(e)}"}


def right_click(x: int = None, y: int = None) -> dict:
    """
    Right click mouse.
    """
    return click(x, y, button="right")


def scroll(amount: int) -> dict:
    """
    Scroll mouse wheel up (positive amount) or down (negative amount).
    """
    try:
        logger.info(f"Scrolling mouse by amount: {amount}")
        pyautogui.scroll(amount)
        return {"status": "SUCCESS", "message": f"Scrolled mouse by {amount}"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Failed scroll: {str(e)}"}
