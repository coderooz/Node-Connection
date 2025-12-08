"""
Configuration management for Network Intelligence application.
"""
import os
from pathlib import Path
from typing import Dict, Any

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Server configuration
HOST = os.getenv("NI_HOST", "127.0.0.1")
PORT = int(os.getenv("NI_PORT", "5000"))
DEBUG = os.getenv("NI_DEBUG", "False").lower() == "true"

# Storage configuration
DATA_DIR = BASE_DIR / "storage"
DEFAULT_NETWORK_FILE = DATA_DIR / "default_network.json"

# Visualization configuration
PHYSICS_CONFIG_FILE = BASE_DIR / "visualization" / "physics_settings.json"

# Application settings
APP_NAME = "Network Intelligence"
VERSION = "2.0.0"

# Logging configuration
LOG_LEVEL = os.getenv("NI_LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "app.log"

# Performance settings
MAX_NODES = int(os.getenv("NI_MAX_NODES", "1000"))
MAX_EDGES = int(os.getenv("NI_MAX_EDGES", "5000"))
CACHE_ENABLED = os.getenv("NI_CACHE_ENABLED", "True").lower() == "true"

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary."""
    return {
        "host": HOST,
        "port": PORT,
        "debug": DEBUG,
        "data_dir": str(DATA_DIR),
        "default_network": str(DEFAULT_NETWORK_FILE),
        "physics_config": str(PHYSICS_CONFIG_FILE),
        "app_name": APP_NAME,
        "version": VERSION,
        "log_level": LOG_LEVEL,
        "max_nodes": MAX_NODES,
        "max_edges": MAX_EDGES,
        "cache_enabled": CACHE_ENABLED,
    }