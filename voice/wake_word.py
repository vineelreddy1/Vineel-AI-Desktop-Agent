import logging
import config

logger = logging.getLogger("VineelAssistant.WakeWord")


class WakeWordDetector:
    def __init__(self, wake_word: str = None):
        self.wake_word = (wake_word or config.WAKE_WORD).lower()
        self.aliases = config.WAKE_WORD_ALIASES

    def set_wake_word(self, wake_word: str):
        self.wake_word = wake_word.lower()
        if self.wake_word not in self.aliases:
            self.aliases.insert(0, self.wake_word)

    def process_input(self, text: str, require_wake_word: bool = True) -> tuple[bool, str]:
        """
        Check if text contains wake word.
        Returns tuple: (is_wake_word_detected, cleaned_command)
        """
        if not text:
            return False, ""

        clean_text = text.strip().lower()

        if not require_wake_word:
            return True, text.strip()

        # Check aliases
        for alias in self.aliases:
            if clean_text.startswith(alias):
                command = clean_text[len(alias):].strip(" ,.-!")
                logger.info(f"Wake word '{alias}' detected! Command extracted: '{command}'")
                return True, command
            elif alias in clean_text:
                idx = clean_text.find(alias)
                command = clean_text[idx + len(alias):].strip(" ,.-!")
                logger.info(f"Wake word '{alias}' detected in sentence! Command extracted: '{command}'")
                return True, command

        return False, ""
