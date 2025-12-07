import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from flask import Flask

from storage import io_manager
from visualization.network_visualizer import NetworkVisualizer
from ui.controller import AppController
from ui.widgets import init_app

# NEW IMPORT
from desktop.tk_app import launch_desktop


def ask_launch_mode() -> str:
    result = {"mode": "browser"}

    dialog = tk.Tk()
    dialog.title("Launch Options")
    dialog.geometry("400x180")

    label = ttk.Label(dialog, text="Select visualization mode:", font=("Segoe UI", 12))
    label.pack(pady=15)

    def select(mode):
        result["mode"] = mode
        dialog.destroy()

    btn_browser = ttk.Button(dialog, text="Open in Browser", width=28, command=lambda: select("browser"))
    btn_browser.pack(pady=5)

    btn_desktop = ttk.Button(dialog, text="Open Desktop App", width=28, command=lambda: select("desktop"))
    btn_desktop.pack(pady=5)

    dialog.mainloop()
    return result["mode"]


def create_app() -> Flask:
    base_dir = Path(__file__).resolve().parent

    graph_model = io_manager.load_or_init_graph(base_dir / "storage" / "default_network.json")

    physics_config_path = base_dir / "visualization" / "physics_settings.json"
    visualizer = NetworkVisualizer(physics_config_path)

    app = Flask(__name__)
    controller = AppController(graph_model, visualizer, io_manager)
    init_app(app, controller, visualizer)

    return app


if __name__ == "__main__":
    mode = ask_launch_mode()

    app = create_app()
    port = 5000
    url = f"http://127.0.0.1:{port}/"
    
    def run_server():
        app.run(host="127.0.0.1", port=port, debug=False)
    
    # Start server backend
    threading.Thread(target=run_server, daemon=True).start()

    # Launch UI based on user choice
    if mode == "desktop":
        launch_desktop(url)
    else:
        webbrowser.open(url)

    # Keep main thread alive
    import time
    while True:
        time.sleep(1)
