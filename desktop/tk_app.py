import threading
import tkinter as tk
from tkinter import ttk
import webbrowser
import webview

try:
    # Python 3.11+ built-in web view support (edgehtml/cef wrapper)
    import tkinterweb
    HAS_WEBVIEW = True
except Exception:
    HAS_WEBVIEW = False


class DesktopApp:
    def __init__(self, url: str):
        self.url = url
        self.root = tk.Tk()
        self.root.title("Network Intelligence (Desktop App)")
        self.root.geometry("1400x900")

        self._setup_ui()

    def _setup_ui(self):
        if HAS_WEBVIEW:
            self._setup_webview()
        else:
            self._fallback_ui()

    def _setup_webview(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        view = tkinterweb.HtmlFrame(frame)
        view.pack(fill="both", expand=True)

        # 🔥 Live UI inside the desktop app!
        view.load_website(self.url)

    def _fallback_ui(self):
        label = ttk.Label(
            self.root,
            text="Embedded webview not available.\nClick button to open in browser.",
            font=("Segoe UI", 13),
            anchor="center"
        )
        label.pack(expand=True)

        btn = ttk.Button(
            self.root,
            text="Open in Browser",
            command=lambda: webbrowser.open(self.url),
        )
        btn.pack(pady=20)

    def run(self):
        self.root.mainloop()


def launch_desktop(url: str):
    # PyWebView automatically embeds a modern browser (WebKit/Edge)
    window = webview.create_window(
        "Network Intelligence",
        url=url,
        width=1600,
        height=900,
        resizable=True,
        fullscreen=False
    )
    webview.start(debug=False)