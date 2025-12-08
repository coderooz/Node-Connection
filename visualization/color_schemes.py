"""
Color schemes and palettes for visualization.
"""
from typing import Dict

# Category-based color mapping
CATEGORY_COLORS: Dict[str, str] = {
    "ai lab": "#a855f7",           # Purple
    "ai": "#a855f7",
    "cloud": "#22c55e",            # Green
    "cloud & software": "#06b6d4", # Cyan
    "cloud & ai": "#3b82f6",       # Blue
    "gpu hardware": "#f97316",     # Orange
    "hardware": "#f97316",
    "cpu / foundry": "#ea580c",    # Deep orange
    "vc": "#eab308",               # Gold
    "investment": "#eab308",
    "startup": "#ec4899",          # Pink
    "robotics": "#8b5cf6",         # Violet
    "ai cloud": "#14b8a6",         # Teal
    "services": "#10b981",         # Emerald
}

# Community color palette (for clustering)
COMMUNITY_COLORS = [
    "#38bdf8",  # Sky blue
    "#a5b4fc",  # Indigo
    "#f97316",  # Orange
    "#22c55e",  # Green
    "#fb7185",  # Rose
    "#eab308",  # Yellow
    "#2dd4bf",  # Teal
    "#f9a8d4",  # Pink
    "#818cf8",  # Blue-violet
    "#34d399",  # Emerald
]

# Edge type color mapping
EDGE_COLORS: Dict[str, str] = {
    "hardware": "rgba(249, 115, 22, 0.95)",      # Orange
    "software": "rgba(59, 130, 246, 0.95)",      # Blue
    "investment": "rgba(234, 179, 8, 0.98)",     # Gold
    "services": "rgba(34, 197, 94, 0.95)",       # Green
    "cloud": "rgba(56, 189, 248, 0.95)",         # Cyan
    "vc": "rgba(236, 72, 153, 0.95)",            # Pink
    "research": "rgba(129, 140, 248, 0.98)",     # Indigo
    "partnership": "rgba(244, 114, 182, 0.95)",  # Rose
    "supply": "rgba(96, 165, 250, 0.95)",        # Soft blue
    "other": "rgba(148, 163, 184, 0.9)",         # Slate
    "unknown": "rgba(148, 163, 184, 0.9)",       # Slate
}

# Default colors
DEFAULT_NODE_COLOR = "#38bdf8"
DEFAULT_EDGE_COLOR = "rgba(148, 163, 184, 0.8)"


def get_category_color(category: str) -> str:
    """
    Get color for a node category.
    
    Args:
        category: Category name
        
    Returns:
        Hex color string
    """
    if not category:
        return DEFAULT_NODE_COLOR
    
    key = category.lower().strip()
    return CATEGORY_COLORS.get(key, DEFAULT_NODE_COLOR)


def get_community_color(community_id: int) -> str:
    """
    Get color for a community ID.
    
    Args:
        community_id: Community index
        
    Returns:
        Hex color string
    """
    if community_id is None:
        return DEFAULT_NODE_COLOR
    
    try:
        idx = int(community_id) % len(COMMUNITY_COLORS)
        return COMMUNITY_COLORS[idx]
    except (TypeError, ValueError):
        return DEFAULT_NODE_COLOR


def get_edge_color(relationship_type: str) -> str:
    """
    Get color for an edge type.
    
    Args:
        relationship_type: Type of relationship
        
    Returns:
        RGBA color string
    """
    if not relationship_type:
        return DEFAULT_EDGE_COLOR
    
    key = relationship_type.lower().strip()
    return EDGE_COLORS.get(key, DEFAULT_EDGE_COLOR)