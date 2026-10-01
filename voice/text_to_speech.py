import logging
import threading
import config

logger = logging.getLogger("VineelAssistant.TTS")

_tts_engine = None
_tts_lock = threading.Lock()


def init_tts():
    global _tts_engine
    if config.TTS_PROVIDER == "mock":
        return None
        
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", config.TTS_RATE)
        if config.TTS_VOICE:
            engine.setProperty("voice", config.TTS_VOICE)
        return engine
    except Exception as e:
        logger.warning(f"Failed to initialize pyttsx3 TTS engine: {e}. Falling back to console output.")
        return None


def speak(text: str):
    """
    Speak response aloud using configured TTS provider.
    Runs non-blocking or safe thread execution.
    """
    if not text:
        return
        
    logger.info(f"Assistant Speech Output: '{text}'")
    try:
        print(f"Assistant: {text}")
    except UnicodeEncodeError:
        print(f"Assistant: {text.encode('ascii', 'ignore').decode('ascii')}")
    
    if config.TTS_PROVIDER == "mock":
        return

    def _speak_thread(text_to_speak):
        with _tts_lock:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty("rate", config.TTS_RATE)
                engine.say(text_to_speak)
                engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS execution error: {e}")

    t = threading.Thread(target=_speak_thread, args=(text,), daemon=True)
    t.start()
