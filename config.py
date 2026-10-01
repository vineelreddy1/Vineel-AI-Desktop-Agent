import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)

# General Settings
APP_NAME = "Vineel Assistant"
VERSION = "1.0.0"

# Directories
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "assistant.log"

SCREENSHOTS_DIR = BASE_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# AI & LLM Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini" if GEMINI_API_KEY else "mock").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")

# Speech to Text Settings
STT_PROVIDER = os.getenv("STT_PROVIDER", "speech_recognition").lower()  # 'speech_recognition', 'whisper', 'mock'
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "en-US")
STT_LISTEN_TIMEOUT = int(os.getenv("STT_LISTEN_TIMEOUT", "5"))
STT_PHRASE_TIME_LIMIT = int(os.getenv("STT_PHRASE_TIME_LIMIT", "8"))

# Text to Speech Settings
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "pyttsx3").lower()  # 'pyttsx3', 'edge_tts', 'mock'
TTS_VOICE = os.getenv("TTS_VOICE", "")
TTS_RATE = int(os.getenv("TTS_RATE", "175"))

# Wake Word Settings
WAKE_WORD_ENABLED = os.getenv("WAKE_WORD_ENABLED", "true").lower() == "true"
WAKE_WORD = os.getenv("WAKE_WORD", "hey vineel").lower()
WAKE_WORD_ALIASES = [WAKE_WORD, "vineel", "hey vinil", "vinil", "hey vneel"]

# Confirmation & Risk Settings
# LOW: Execute automatically
# MEDIUM: Require prompt confirmation
# HIGH: Require explicit prompt confirmation + confirmation log
RISK_LEVELS = {
    "LOW": ["open_application", "type_text", "press_key", "hotkey", "open_url", 
            "search_web", "go_back", "go_forward", "refresh_page", "new_tab", 
            "close_tab", "list_windows", "get_active_window", "focus_window", 
            "minimize_window", "maximize_window", "take_screenshot", "get_screen_size",
            "move_mouse", "click", "double_click", "right_click", "scroll"],
    "MEDIUM": ["close_application", "restart_application", "close_window"],
    "HIGH": ["execute_shell_command", "delete_file", "shutdown_system", "reboot_system"]
}
