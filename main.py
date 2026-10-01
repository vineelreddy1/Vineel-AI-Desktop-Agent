import sys
import time
import argparse
import logging
import config

# Initialize Root Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("VineelAssistant.Main")

from assistant.agent import Agent
from voice.speech_to_text import SpeechToText
from voice.wake_word import WakeWordDetector
from ui.dashboard import launch_gui


def run_text_mode():
    """
    CLI Text Mode for testing natural language commands without microphone input.
    """
    print(f"\n==================================================")
    print(f"   {config.APP_NAME} v{config.VERSION} - CLI Test Mode")
    print(f"==================================================")
    print("Type your desktop command (e.g., 'Open Chrome', 'Type YouTube', 'Press enter', 'Open YouTube').")
    print("Type 'exit' or 'quit' to exit.\n")

    agent = Agent()

    while True:
        try:
            cmd = input("Vineel User > ").strip()
            if not cmd:
                continue
            if cmd.lower() in ["exit", "quit", "q"]:
                print("Exiting Vineel Assistant. Goodbye!")
                break
                
            res = agent.execute_command(cmd)
            print(f"Result: {res.get('status')} - {res.get('message', 'Completed')}\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error in text mode execution: {e}")


def run_voice_mode():
    """
    Headless Voice Assistant mode continuously listening for wake word & commands.
    """
    print(f"\n==================================================")
    print(f"   {config.APP_NAME} v{config.VERSION} - Continuous Voice Mode")
    print(f"==================================================")
    print(f"Wake word: '{config.WAKE_WORD}'")
    print("Listening... Press Ctrl+C to stop.\n")

    stt = SpeechToText()
    wake_detector = WakeWordDetector()
    agent = Agent()

    while True:
        try:
            spoken = stt.listen_command()
            if spoken:
                logger.info(f"Voice input heard: '{spoken}'")
                is_wake, clean_cmd = wake_detector.process_input(spoken, require_wake_word=config.WAKE_WORD_ENABLED)
                if is_wake and clean_cmd:
                    agent.execute_command(clean_cmd)
                elif is_wake and not clean_cmd:
                    print("Listening for your command...")
        except KeyboardInterrupt:
            print("\nStopping voice assistant...")
            break
        except Exception as e:
            logger.error(f"Error in voice mode: {e}")
            time.sleep(1.0)


def main():
    parser = argparse.ArgumentParser(description="Vineel Assistant Desktop AI Voice Agent")
    parser.add_argument("--text", action="store_true", help="Launch interactive CLI text command mode")
    parser.add_argument("--voice", action="store_true", help="Launch continuous background voice mode")
    parser.add_argument("--gui", action="store_true", help="Launch Graphical Dashboard UI (default)")

    args = parser.parse_args()

    logger.info(f"Starting {config.APP_NAME} v{config.VERSION}")

    if args.text:
        run_text_mode()
    elif args.voice:
        run_voice_mode()
    else:
        # Default mode is GUI if PySide6 is available, else CLI text mode
        try:
            launch_gui()
        except Exception as e:
            logger.warning(f"Failed to launch GUI ({e}). Falling back to text mode.")
            run_text_mode()


if __name__ == "__main__":
    main()
