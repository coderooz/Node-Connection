from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from model import GraphModel


class NetworkVisualizer:
    """
    Prepares WebGL/3D-friendly graph data & visual styling for the frontend.

    - Reads physics + theme from physics_settings.json
    - Computes node sizes from influence
    - Colors nodes by community/category
    - Colors edges by relationship type
    """

    def __init__(self, physics_config_path: Path) -> None:
        self.config_path = physics_config_path
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {
                "backgroundColor": "#050816",
                "nodeSizeMin": 4,
                "nodeSizeMax": 18,
                "linkCurvature": 0.25,
                "linkOpacity": 0.8,
                "linkWidthFactor": 3.5,
                "arrowLength": 4,
                "particleSpeed": 0.006,
                "velocityDecay": 0.25,
            }
        with self.config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # ---------- Public ----------

    def build_graph_data(self, model: GraphModel) -> Dict[str, Any]:
        graph = model.graph
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        # Pre-calc node sizes
        size_min = self.config.get("nodeSizeMin", 4)
        size_max = self.config.get("nodeSizeMax", 18)

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

            influence = float(data.get("influence", 0.01))
            size = size_min + influence * (size_max - size_min)

            community = data.get("community")
            category = base.get("category")

            community_color = self._color_for_community(community)
            category_color = self._color_for_category(category)

            tooltip = self._build_tooltip(base, influence, community)

            base.update(
                {
                    "size": size,
                    "influence": influence,
                    "community": community,
                    "community_color": community_color,
                    "category_color": category_color,
                    "tooltip": tooltip,
                }
            )
            nodes.append(base)

        for u, v, edata in graph.edges(data=True):
            rel_type = edata.get("relationship_type", "other")
            impact = float(edata.get("impact", 0.5))
            color = self._color_for_edge_type(rel_type)
            edge = {
                "source": u,
                "target": v,
                "relationship_type": rel_type,
                "impact": impact,
                "directed": edata.get("directed", True),
                "metadata": edata.get("metadata", {}),
                "color": color,
                "curvature": self.config.get("linkCurvature", 0.25),
            }
            edges.append(edge)

        return {
            "nodes": nodes,
            "links": edges,
        }

    # ---------- Helpers ----------

    def _color_for_community(self, community: Any) -> str:
        palette = [
            "#38bdf8",
            "#a5b4fc",
            "#f97316",
            "#22c55e",
            "#fb7185",
            "#eab308",
            "#2dd4bf",
            "#f9a8d4",
        ]
        if community is None:
            return "#38bdf8"
        try:
            idx = int(community) % len(palette)
        except (TypeError, ValueError):
            idx = 0
        return palette[idx]

    def _color_for_category(self, category: Any) -> str:
        if not category:
            return "#38bdf8"
        key = str(category).lower()
        if "gpu" in key or "hardware" in key:
            return "#f97316"
        if "cloud" in key or "infra" in key:
            return "#22c55e"
        if "ai" in key or "lab" in key or "model" in key:
            return "#a855f7"
        if "vc" in key or "invest" in key or "fund" in key:
            return "#eab308"
        if "startup" in key:
            return "#ec4899"
        return "#38bdf8"

    def _color_for_edge_type(self, rel_type: str) -> str:
        key = (rel_type or "").lower()
        if key == "hardware":
            return "rgba(249, 115, 22, 0.95)"      # orange
        if key == "software":
            return "rgba(59, 130, 246, 0.95)"      # blue
        if key == "investment":
            return "rgba(234, 179, 8, 0.98)"       # gold
        if key == "services":
            return "rgba(34, 197, 94, 0.95)"       # green
        if key == "cloud":
            return "rgba(56, 189, 248, 0.95)"      # cyan
        if key == "vc":
            return "rgba(236, 72, 153, 0.95)"      # pink
        if key == "research":
            return "rgba(129, 140, 248, 0.98)"     # indigo
        if key == "partnership":
            return "rgba(244, 114, 182, 0.95)"     # rose
        if key == "supply":
            return "rgba(96, 165, 250, 0.95)"      # soft blue
        return "rgba(148, 163, 184, 0.9)"          # default slate

    def _build_tooltip(self, node: Dict[str, Any], influence: float, community: Any) -> str:
        parts = []
        parts.append(f"<b>{node.get('label', node.get('id'))}</b>")
        if node.get("category"):
            parts.append(f"Category: {node['category']}")
        if node.get("role"):
            parts.append(f"Role: {node['role']}")
        if node.get("company_type"):
            parts.append(f"Type: {node['company_type']}")
        if node.get("valuation") is not None:
            parts.append(f"Valuation: ${node['valuation']:,.0f}")
        parts.append(f"Influence: {influence:.3f}")
        if community is not None:
            parts.append(f"Cluster: {community}")
        return "<br/>".join(parts)
