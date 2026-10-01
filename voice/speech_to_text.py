import logging
import config

logger = logging.getLogger("VineelAssistant.STT")

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False


class SpeechToText:
    def __init__(self):
        self.provider = config.STT_PROVIDER
        self.recognizer = None
        self.microphone = None
        
        if HAS_SR and self.provider != "mock":
            try:
                self.recognizer = sr.Recognizer()
                # Check microphone availability
                mics = sr.Microphone.list_microphone_names()
                if mics:
                    self.microphone = sr.Microphone()
                    logger.info(f"Initialized microphone: {mics[0]}")
                else:
                    logger.warning("No microphone found on system.")
            except Exception as e:
                logger.warning(f"Microphone initialization failed: {e}")

    def listen_command(self, timeout: int = None, phrase_time_limit: int = None) -> str:
        """
        Listen from microphone and transcribe speech to text.
        Returns transcribed string or empty string on silence/error.
        """
        timeout = timeout or config.STT_LISTEN_TIMEOUT
        phrase_time_limit = phrase_time_limit or config.STT_PHRASE_TIME_LIMIT

        if not HAS_SR or not self.microphone or self.provider == "mock":
            logger.debug("STT running in fallback/mock mode.")
            return ""

        try:
            with self.microphone as source:
                logger.info("Listening for voice input...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
            logger.info("Processing speech recognition...")
            text = self.recognizer.recognize_google(audio, language=config.STT_LANGUAGE)
            logger.info(f"Recognized Speech: '{text}'")
            return text.strip()

        except sr.WaitTimeoutError:
            logger.debug("Listening timed out waiting for phrase.")
            return ""
        except sr.UnknownValueError:
            logger.debug("Speech recognition could not understand audio.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            return ""
