"""
Network visualization data preparation.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

from core.graph_model import GraphModel
from .color_schemes import (
    get_category_color,
    get_community_color,
    get_edge_color
)
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkVisualizer:
    """
    Prepares graph data for 3D visualization.
    
    Handles:
    - Node sizing based on influence
    - Color assignment (category/community)
    - Edge styling by relationship type
    - Tooltip generation
    """
    
    def __init__(self, physics_config_path: Path) -> None:
        """
        Initialize visualizer.
        
        Args:
            physics_config_path: Path to physics configuration JSON
        """
        self.config_path = physics_config_path
        self.config: Dict[str, Any] = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load physics configuration from JSON file."""
        if not self.config_path.exists():
            logger.warning(f"Physics config not found: {self.config_path}. Using defaults.")
            return self._get_default_config()
        
        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info(f"Loaded physics config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading physics config: {e}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default physics configuration."""
        return {
            "backgroundColor": "#050816",
            "nodeSizeMin": 4,
            "nodeSizeMax": 20,
            "linkCurvature": 0.3,
            "linkOpacity": 0.8,
            "linkWidthFactor": 3.5,
            "arrowLength": 5,
            "particleSpeed": 0.007,
            "velocityDecay": 0.25,
        }
    
    def build_graph_data(self, model: GraphModel) -> Dict[str, Any]:
        """
        Build visualization-ready graph data.
        
        Args:
            model: GraphModel instance
            
        Returns:
            Dictionary with nodes and links arrays
        """
        graph = model.graph
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        
        # Configuration
        size_min = self.config.get("nodeSizeMin", 4)
        size_max = self.config.get("nodeSizeMax", 20)
        
        # Build nodes
        for node_id, data in graph.nodes(data=True):
            node_obj = data.get("node")
            if node_obj:
                base = node_obj.to_dict()
            else:
                base = {
                    "id": node_id,
                    "label": data.get("label", node_id),
                    "category": data.get("category"),
                    "valuation": data.get("valuation"),
                    "role": data.get("role"),
                    "company_type": data.get("company_type"),
                    "logo_url": data.get("logo_url"),
                    "metadata": data.get("metadata", {}),
                }
            
            # Compute node size from influence
            influence = float(data.get("influence", 0.01))
            size = size_min + influence * (size_max - size_min)
            
            # Get community and category
            community = data.get("community")
            category = base.get("category")
            
            # Assign colors
            community_color = get_community_color(community)
            category_color = get_category_color(category)
            
            # Build tooltip
            tooltip = self._build_tooltip(base, influence, community)
            
            # Add visualization attributes
            base.update({
                "size": size,
                "influence": influence,
                "community": community,
                "community_color": community_color,
                "category_color": category_color,
                "tooltip": tooltip,
            })
            
            nodes.append(base)
        
        # Build edges
        for u, v, edata in graph.edges(data=True):
            rel_type = edata.get("relationship_type", "other")
            impact = float(edata.get("impact", 0.5))
            color = get_edge_color(rel_type)
            
            edge = {
                "source": u,
                "target": v,
                "relationship_type": rel_type,
                "impact": impact,
                "directed": edata.get("directed", True),
                "metadata": edata.get("metadata", {}),
                "color": color,
                "curvature": self.config.get("linkCurvature", 0.3),
            }
            edges.append(edge)
        
        logger.debug(f"Built visualization data: {len(nodes)} nodes, {len(edges)} edges")
        
        return {
            "nodes": nodes,
            "links": edges,
        }
    
    def _build_tooltip(self, node: Dict[str, Any], 
                      influence: float, 
                      community: Any) -> str:
        """
        Build HTML tooltip for a node.
        
        Args:
            node: Node data dictionary
            influence: Influence score
            community: Community ID
            
        Returns:
            HTML string for tooltip
        """
        parts = []
        
        # Name/Label
        parts.append(f"<b>{node.get('label', node.get('id'))}</b>")
        
        # Category
        if node.get("category"):
            parts.append(f"Category: {node['category']}")
        
        # Role
        if node.get("role"):
            parts.append(f"Role: {node['role']}")
        
        # Type
        if node.get("company_type"):
            parts.append(f"Type: {node['company_type']}")
        
        # Valuation
        if node.get("valuation") is not None:
            val = node['valuation']
            if val >= 1e9:
                formatted = f"${val/1e9:.1f}B"
            elif val >= 1e6:
                formatted = f"${val/1e6:.1f}M"
            else:
                formatted = f"${val:,.0f}"
            parts.append(f"Valuation: {formatted}")
        
        # Analytics
        parts.append(f"Influence: {influence:.3f}")
        
        if community is not None:
            parts.append(f"Community: {community}")
        
        return "<br/>".join(parts)