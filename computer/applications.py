import os
import shutil
import subprocess
import logging
from pathlib import Path
import psutil

try:
    import win32gui
    import win32process
    import win32con
    import winreg
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

logger = logging.getLogger("VineelAssistant.Applications")

# Known application aliases and target executable names
APP_ALIASES = {
    "chrome": ["chrome.exe", "Google Chrome"],
    "google chrome": ["chrome.exe", "Google Chrome"],
    "chrome browser": ["chrome.exe", "Google Chrome"],
    "edge": ["msedge.exe", "Microsoft Edge"],
    "microsoft edge": ["msedge.exe", "Microsoft Edge"],
    "ms edge": ["msedge.exe", "Microsoft Edge"],
    "firefox": ["firefox.exe", "Mozilla Firefox"],
    "mozilla firefox": ["firefox.exe", "Mozilla Firefox"],
    "notepad": ["notepad.exe", "Notepad"],
    "calculator": ["calc.exe", "Calculator"],
    "calc": ["calc.exe", "Calculator"],
    "file explorer": ["explorer.exe", "File Explorer"],
    "explorer": ["explorer.exe", "File Explorer"],
    "my computer": ["explorer.exe", "File Explorer"],
    "vs code": ["code.cmd", "code.exe", "Visual Studio Code"],
    "vscode": ["code.cmd", "code.exe", "Visual Studio Code"],
    "code": ["code.cmd", "code.exe", "Visual Studio Code"],
    "cmd": ["cmd.exe", "Command Prompt"],
    "command prompt": ["cmd.exe", "Command Prompt"],
    "terminal": ["cmd.exe", "Command Prompt"],
    "powershell": ["powershell.exe", "Windows PowerShell"],
}


def search_windows_registry_app_paths(exe_name: str) -> str | None:
    """
    Search Windows Registry App Paths for executable path.
    """
    if not HAS_WIN32:
        return None

    subkeys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
    ]

    for root_key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for subkey in subkeys:
            try:
                key_path = f"{subkey}\\{exe_name}"
                with winreg.OpenKey(root_key, key_path) as k:
                    val, _ = winreg.QueryValueEx(k, "")
                    if val and os.path.exists(val):
                        return val
            except (OSError, FileNotFoundError):
                pass
    return None


def search_start_menu_shortcuts(app_alias: str) -> str | None:
    """
    Search Windows Start Menu shortcuts for application match.
    """
    system_start = Path(os.environ.get("ProgramData", "C:\\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    user_start = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    
    clean_alias = app_alias.strip().lower()
    if not clean_alias or len(clean_alias) < 2:
        return None

    for base in [system_start, user_start]:
        if base.exists():
            for shortcut in base.rglob("*.lnk"):
                stem = shortcut.stem.lower()
                if clean_alias == stem or stem.startswith(f"{clean_alias} ") or f" {clean_alias}" in stem:
                    return str(shortcut)
    return None


def find_executable_path(app_identifier: str) -> str | None:
    """
    Locate valid executable path or return None if application is not installed.
    """
    clean_name = app_identifier.strip().lower()
    target_names = APP_ALIASES.get(clean_name, [clean_name, f"{clean_name}.exe"])

    for name in target_names:
        # 1. System PATH
        found = shutil.which(name)
        if found:
            return found

        # 2. Windows Registry
        if not name.endswith(".exe"):
            reg_found = search_windows_registry_app_paths(f"{name}.exe")
        else:
            reg_found = search_windows_registry_app_paths(name)
        if reg_found:
            return reg_found

        # 3. Standard Windows Directories
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        system_root = os.environ.get("SystemRoot", "C:\\Windows")

        exe_filename = name if name.endswith(".exe") else f"{name}.exe"

        possible_paths = [
            Path(system_root) / "System32" / exe_filename,
            Path(system_root) / exe_filename,
            Path(program_files) / "Google" / "Chrome" / "Application" / exe_filename,
            Path(program_files_x86) / "Google" / "Chrome" / "Application" / exe_filename,
            Path(program_files) / "Microsoft" / "Edge" / "Application" / exe_filename,
            Path(program_files_x86) / "Microsoft" / "Edge" / "Application" / exe_filename,
            Path(program_files) / "Mozilla Firefox" / exe_filename,
            Path(program_files_x86) / "Mozilla Firefox" / exe_filename,
            Path(local_app_data) / "Programs" / "Microsoft VS Code" / exe_filename,
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        # 4. Start Menu shortcuts
        shortcut = search_start_menu_shortcuts(clean_name)
        if shortcut:
            return shortcut

    return None


def is_application_running(app_name: str) -> bool:
    """
    Check if an application is running.
    """
    clean_name = app_name.strip().lower()
    targets = APP_ALIASES.get(clean_name, [clean_name, f"{clean_name}.exe"])
    target_exes = [t.lower() for t in targets if t.endswith(".exe")]

    try:
        for proc in psutil.process_iter(['name']):
            proc_name = (proc.info['name'] or "").lower()
            if any(t == proc_name or t in proc_name for t in target_exes):
                return True
            if clean_name in proc_name:
                return True
    except Exception as e:
        logger.error(f"Error checking process for {app_name}: {e}")
    return False


def open_application(app_name: str) -> dict:
    """
    Launch an application on Windows safely.
    If application is not installed/found, returns clean error response without fallback execution.
    """
    clean_name = app_name.strip().lower()
    logger.info(f"Attempting to open application: {clean_name}")

    # Built-in Windows app handlers
    if clean_name in ["file explorer", "explorer", "my computer"]:
        subprocess.Popen(["explorer.exe"])
        return {"status": "SUCCESS", "message": "Opened File Explorer"}
    elif clean_name in ["calculator", "calc"]:
        subprocess.Popen(["calc.exe"])
        return {"status": "SUCCESS", "message": "Opened Calculator"}
    elif clean_name in ["notepad"]:
        subprocess.Popen(["notepad.exe"])
        return {"status": "SUCCESS", "message": "Opened Notepad"}
    elif clean_name in ["cmd", "command prompt"]:
        subprocess.Popen(["cmd.exe"])
        return {"status": "SUCCESS", "message": "Opened Command Prompt"}
    elif clean_name in ["powershell"]:
        subprocess.Popen(["powershell.exe"])
        return {"status": "SUCCESS", "message": "Opened Windows PowerShell"}

    exe_path = find_executable_path(clean_name)

    if not exe_path:
        error_msg = f"I couldn't find {app_name} installed on this computer."
        logger.warning(error_msg)
        return {"status": "FAILED", "message": error_msg}

    try:
        if exe_path.endswith(".lnk"):
            os.startfile(exe_path)
        else:
            subprocess.Popen([exe_path])
        return {"status": "SUCCESS", "message": f"Successfully launched {app_name}"}
    except Exception as e:
        error_msg = f"Failed to launch {app_name}: {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def close_application(app_name: str) -> dict:
    """
    Terminate process matching application name.
    """
    clean_name = app_name.strip().lower()
    logger.info(f"Closing application: {clean_name}")
    targets = APP_ALIASES.get(clean_name, [clean_name, f"{clean_name}.exe"])
    target_exes = [t.lower() for t in targets if t.endswith(".exe")]

    closed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            proc_name = (proc.info['name'] or "").lower()
            if any(t == proc_name for t in target_exes) or (clean_name in proc_name and proc_name != "python.exe"):
                try:
                    proc.terminate()
                    closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        if closed_count > 0:
            return {"status": "SUCCESS", "message": f"Closed {closed_count} process(es) for {app_name}"}
        else:
            first_exe = target_exes[0] if target_exes else f"{clean_name}.exe"
            subprocess.run(["taskkill", "/F", "/IM", first_exe], capture_output=True)
            return {"status": "SUCCESS", "message": f"Sent close signal to {app_name}"}
    except Exception as e:
        error_msg = f"Failed to close application '{app_name}': {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def restart_application(app_name: str) -> dict:
    close_res = close_application(app_name)
    open_res = open_application(app_name)
    return {"status": "SUCCESS", "message": f"Restarted {app_name}"}


def focus_application(app_name: str) -> dict:
    clean_name = app_name.strip().lower()
    if not HAS_WIN32:
        return {"status": "FAILED", "message": "win32gui not available"}

    matched_hwnd = []
    def enum_windows_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).lower()
            if clean_name in title or any(alias in title for alias in APP_ALIASES.get(clean_name, [])):
                matched_hwnd.append(hwnd)

    try:
        win32gui.EnumWindows(enum_windows_callback, None)
        if matched_hwnd:
            hwnd = matched_hwnd[0]
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return {"status": "SUCCESS", "message": f"Focused {app_name}"}
        else:
            return {"status": "FAILED", "message": f"No active window found matching '{app_name}'"}
    except Exception as e:
        return {"status": "FAILED", "message": f"Error focusing {app_name}: {str(e)}"}
