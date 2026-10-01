import urllib.parse
import webbrowser
import logging
from computer.keyboard import hotkey, type_text, press_key

logger = logging.getLogger("VineelAssistant.Browser")


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        if "." in url and not " " in url:
            url = "https://" + url
        else:
            url = f"https://www.google.com/search?q={urllib.parse.quote(url)}"
    return url


def open_url(url: str) -> dict:
    """
    Open specified URL in the default browser.
    """
    try:
        final_url = normalize_url(url)
        logger.info(f"Opening URL: {final_url}")
        webbrowser.open(final_url)
        return {"status": "SUCCESS", "url": final_url, "message": f"Opened {final_url}"}
    except Exception as e:
        error_msg = f"Failed to open URL '{url}': {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def search_web(query: str, engine: str = "google") -> dict:
    """
    Search the web for query using google or youtube.
    """
    try:
        clean_q = query.strip()
        encoded = urllib.parse.quote(clean_q)
        
        if "youtube" in engine.lower() or "youtube" in clean_q.lower():
            url = f"https://www.youtube.com/results?search_query={encoded}"
        else:
            url = f"https://www.google.com/search?q={encoded}"
            
        logger.info(f"Searching web ({engine}): '{clean_q}' -> {url}")
        webbrowser.open(url)
        return {"status": "SUCCESS", "query": clean_q, "url": url, "message": f"Searched for '{clean_q}'"}
    except Exception as e:
        error_msg = f"Failed to search web for '{query}': {str(e)}"
        logger.error(error_msg)
        return {"status": "FAILED", "message": error_msg}


def go_back() -> dict:
    """
    Navigate browser back.
    """
    res = hotkey(["alt", "left"])
    if res["status"] == "SUCCESS":
        res["message"] = "Navigated back in browser"
    return res


def go_forward() -> dict:
    """
    Navigate browser forward.
    """
    res = hotkey(["alt", "right"])
    if res["status"] == "SUCCESS":
        res["message"] = "Navigated forward in browser"
    return res


def refresh_page() -> dict:
    """
    Refresh browser page.
    """
    res = hotkey(["ctrl", "r"])
    if res["status"] == "SUCCESS":
        res["message"] = "Refreshed browser page"
    return res


def new_tab() -> dict:
    """
    Open a new browser tab.
    """
    res = hotkey(["ctrl", "t"])
    if res["status"] == "SUCCESS":
        res["message"] = "Opened new browser tab"
    return res


def close_tab() -> dict:
    """
    Close current browser tab.
    """
    res = hotkey(["ctrl", "w"])
    if res["status"] == "SUCCESS":
        res["message"] = "Closed browser tab"
    return res
