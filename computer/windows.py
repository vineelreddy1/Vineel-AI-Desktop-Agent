import logging
try:
    import pygetwindow as gw
    HAS_GW = True
except ImportError:
    HAS_GW = False

try:
    import win32gui
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

logger = logging.getLogger("VineelAssistant.Windows")


def list_windows() -> dict:
    """
    List all active visible windows on the screen.
    """
    try:
        windows_list = []
        if HAS_GW:
            all_wins = gw.getAllTitles()
            windows_list = [w for w in all_wins if w.strip()]
        elif HAS_WIN32:
            def enum_cb(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd)
                    if t.strip():
                        windows_list.append(t)
            win32gui.EnumWindows(enum_cb, None)
            
        return {"status": "SUCCESS", "data": windows_list, "message": f"Found {len(windows_list)} visible windows"}
    except Exception as e:
        error_msg = f"Failed to list windows: {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def get_active_window() -> dict:
    """
    Get title of currently active window.
    """
    try:
        if HAS_GW:
            active_win = gw.getActiveWindow()
            if active_win:
                return {"status": "SUCCESS", "data": active_win.title, "message": f"Active window: {active_win.title}"}
        if HAS_WIN32:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return {"status": "SUCCESS", "data": title, "message": f"Active window: {title}"}
        return {"status": "FAILED", "message": "Window APIs unavailable"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Error getting active window: {str(e)}"}


def focus_window(window_name: str) -> dict:
    """
    Focus a window by title substring.
    """
    try:
        clean_target = window_name.strip().lower()
        if HAS_GW:
            matching = [w for w in gw.getAllWindows() if clean_target in w.title.lower()]
            if matching:
                target = matching[0]
                target.activate()
                return {"status": "SUCCESS", "message": f"Activated window: {target.title}"}
                
        if HAS_WIN32:
            found_hwnd = []
            def enum_cb(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd)
                    if clean_target in t.lower():
                        found_hwnd.append(hwnd)
            win32gui.EnumWindows(enum_cb, None)
            if found_hwnd:
                hwnd = found_hwnd[0]
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return {"status": "SUCCESS", "message": f"Focused window matching '{window_name}'"}
                
        return {"status": "FAILED", "message": f"No window found matching '{window_name}'"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Failed to focus window: {str(e)}"}


def minimize_window(window_name: str = None) -> dict:
    """
    Minimize target window or current active window.
    """
    try:
        if not window_name:
            if HAS_GW:
                act = gw.getActiveWindow()
                if act:
                    act.minimize()
                    return {"status": "SUCCESS", "message": f"Minimized active window '{act.title}'"}
            if HAS_WIN32:
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                return {"status": "SUCCESS", "message": "Minimized active window"}
        else:
            res = focus_window(window_name)
            if res["status"] == "SUCCESS":
                if HAS_GW:
                    act = gw.getActiveWindow()
                    if act:
                        act.minimize()
                        return {"status": "SUCCESS", "message": f"Minimized window '{window_name}'"}
        return {"status": "FAILED", "message": "Unable to minimize window"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Error minimizing window: {str(e)}"}


def maximize_window(window_name: str = None) -> dict:
    """
    Maximize target window or current active window.
    """
    try:
        if not window_name:
            if HAS_GW:
                act = gw.getActiveWindow()
                if act:
                    act.maximize()
                    return {"status": "SUCCESS", "message": f"Maximized active window '{act.title}'"}
            if HAS_WIN32:
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                return {"status": "SUCCESS", "message": "Maximized active window"}
        else:
            res = focus_window(window_name)
            if res["status"] == "SUCCESS":
                if HAS_GW:
                    act = gw.getActiveWindow()
                    if act:
                        act.maximize()
                        return {"status": "SUCCESS", "message": f"Maximized window '{window_name}'"}
        return {"status": "FAILED", "message": "Unable to maximize window"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Error maximizing window: {str(e)}"}


def close_window(window_name: str = None) -> dict:
    """
    Close window matching title or currently active window.
    """
    try:
        if not window_name:
            if HAS_GW:
                act = gw.getActiveWindow()
                if act:
                    act.close()
                    return {"status": "SUCCESS", "message": f"Closed window '{act.title}'"}
            if HAS_WIN32:
                hwnd = win32gui.GetForegroundWindow()
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                return {"status": "SUCCESS", "message": "Closed active window"}
        else:
            if HAS_GW:
                clean_target = window_name.strip().lower()
                matching = [w for w in gw.getAllWindows() if clean_target in w.title.lower()]
                if matching:
                    matching[0].close()
                    return {"status": "SUCCESS", "message": f"Closed window '{matching[0].title}'"}
        return {"status": "FAILED", "message": f"Window '{window_name}' not found to close"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Error closing window: {str(e)}"}
