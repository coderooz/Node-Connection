"""
Network Intelligence - Main Application Entry Point
A professional 3D network visualization system.
"""
import sys
import threading
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox
from flask import Flask

# Import configuration
import config
from utils.logger import setup_logger, get_logger
from storage.io_manager import load_or_init_graph
from visualization.network_visualizer import NetworkVisualizer
from api.controllers import AppController
from api.routes import init_routes

# Setup logging
setup_logger()
logger = get_logger(__name__)


class LaunchDialog:
    """Launch mode selection dialog."""
    
    def __init__(self):
        self.result = "browser"
        self.root = None
    
    def show(self) -> str:
        """Display dialog and return selected mode."""
        self.root = tk.Tk()
        self.root.title(f"{config.APP_NAME} - Launch Options")
        self.root.geometry("450x220")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.root.winfo_screenheight() // 2) - (220 // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Title
        title_frame = ttk.Frame(self.root, padding="20")
        title_frame.pack(fill="x")
        
        ttk.Label(
            title_frame,
            text=config.APP_NAME,
            font=("Segoe UI", 16, "bold")
        ).pack()
        
        ttk.Label(
            title_frame,
            text=f"Version {config.VERSION}",
            font=("Segoe UI", 9),
            foreground="gray"
        ).pack()
        
        # Description
        desc_frame = ttk.Frame(self.root, padding="10 0")
        desc_frame.pack(fill="x")
        
        ttk.Label(
            desc_frame,
            text="Choose how to launch the visualization:",
            font=("Segoe UI", 10)
        ).pack()
        
        # Buttons
        btn_frame = ttk.Frame(self.root, padding="20")
        btn_frame.pack(fill="x")
        
        browser_btn = ttk.Button(
            btn_frame,
            text="🌐 Open in Browser (Recommended)",
            command=lambda: self._select("browser"),
            width=35
        )
        browser_btn.pack(pady=5)
        
        desktop_btn = ttk.Button(
            btn_frame,
            text="🖥️  Open Desktop Application",
            command=lambda: self._select("desktop"),
            width=35
        )
        desktop_btn.pack(pady=5)
        
        # Info
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill="x", side="bottom")
        
        ttk.Label(
            info_frame,
            text="Browser mode recommended for best compatibility",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Set focus
        browser_btn.focus_set()
        
        self.root.mainloop()
        return self.result
    
    def _select(self, mode: str):
        """Handle mode selection."""
        self.result = mode
        if self.root:
            self.root.destroy()
    
    def _on_close(self):
        """Handle window close."""
        if self.root:
            self.root.destroy()
        sys.exit(0)


def create_flask_app() -> Flask:
    """Create and configure Flask application."""
    logger.info("Initializing Flask application...")
    
    # Load or create graph model
    graph_model = load_or_init_graph(config.DEFAULT_NETWORK_FILE)
    logger.info(f"Loaded graph: {graph_model.summary()[0]} nodes, {graph_model.summary()[1]} edges")
    
    # Initialize visualizer
    visualizer = NetworkVisualizer(config.PHYSICS_CONFIG_FILE)
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder='ui/web/templates',
                static_folder='ui/web/static')
    
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['JSON_SORT_KEYS'] = False
    
    # Initialize controller and routes
    controller = AppController(graph_model, visualizer)
    init_routes(app, controller, visualizer)
    
    logger.info("Flask application initialized successfully")
    return app


def run_server(app: Flask, host: str, port: int):
    """Run Flask server in a separate thread."""
    try:
        logger.info(f"Starting server on http://{host}:{port}")
        app.run(host=host, port=port, debug=config.DEBUG, use_reloader=False)
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


def launch_browser(url: str):
    """Launch browser with slight delay to ensure server is ready."""
    import time
    time.sleep(1.5)  # Wait for server to start
    logger.info(f"Opening browser: {url}")
    webbrowser.open(url)


def launch_desktop(url: str):
    """Launch desktop application."""
    try:
        from ui.desktop.tk_app import launch_desktop_app
        logger.info("Launching desktop application...")
        launch_desktop_app(url)
    except ImportError as e:
        logger.error(f"Desktop app dependencies not available: {e}")
        messagebox.showerror(
            "Missing Dependencies",
            "Desktop mode requires 'pywebview'. Install it with:\npip install pywebview\n\nLaunching browser instead..."
        )
        launch_browser(url)
    except Exception as e:
        logger.error(f"Failed to launch desktop app: {e}")
        messagebox.showerror(
            "Launch Error",
            f"Failed to launch desktop app:\n{e}\n\nLaunching browser instead..."
        )
        launch_browser(url)


def main():
    """Main application entry point."""
    try:
        logger.info(f"Starting {config.APP_NAME} v{config.VERSION}")
        
        # Show launch dialog
        dialog = LaunchDialog()
        mode = dialog.show()
        
        logger.info(f"Launch mode selected: {mode}")
        
        # Create Flask app
        app = create_flask_app()
        
        # Server URL
        url = f"http://{config.HOST}:{config.PORT}/"
        
        # Start server in background thread
        server_thread = threading.Thread(
            target=run_server,
            args=(app, config.HOST, config.PORT),
            daemon=True
        )
        server_thread.start()
        
        # Launch UI based on mode
        if mode == "desktop":
            launch_desktop(url)
        else:
            launch_browser(url)
        
        # Keep main thread alive
        logger.info("Application running. Press Ctrl+C to exit.")
        try:
            while True:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            sys.exit(0)
            
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()