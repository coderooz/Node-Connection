"""
Desktop application using pywebview for native window.
"""
import sys
from typing import Optional

try:
    import webview
    HAS_WEBVIEW = True
except ImportError:
    HAS_WEBVIEW = False

from utils.logger import get_logger

logger = get_logger(__name__)


def launch_desktop_app(url: str) -> None:
    """
    Launch desktop application with embedded browser.
    
    Args:
        url: URL to load in webview
        
    Raises:
        ImportError: If pywebview is not installed
    """
    if not HAS_WEBVIEW:
        raise ImportError(
            "pywebview is required for desktop mode. "
            "Install it with: pip install pywebview"
        )
    
    logger.info(f"Launching desktop app: {url}")
    
    try:
        # Create window
        window = webview.create_window(
            title="Network Intelligence",
            url=url,
            width=1600,
            height=900,
            resizable=True,
            fullscreen=False,
            min_size=(1024, 768),
        )
        
        # Start webview
        webview.start(debug=False)
        
    except Exception as e:
        logger.error(f"Error launching desktop app: {e}")
        raise