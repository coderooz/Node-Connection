from __future__ import annotations

from typing import Any, Dict, Optional

from model import GraphModel, Node
from visualization.network_visualizer import NetworkVisualizer
from storage import io_manager


class AppController:
    """
    Connects UI actions to the GraphModel and visualization.

    All mutations:
    - Update the in-memory graph
    - Recompute analytics when needed
    - Persist to JSON
    """

    def __init__(
        self,
        graph_model: GraphModel,
        visualizer: NetworkVisualizer,
        io_module: Any,
    ) -> None:
        self.model = graph_model
        self.visualizer = visualizer
        self.io_module = io_module

    # ---------- Graph / visualization ----------

    def get_graph_payload(self) -> Dict[str, Any]:
        """
        Called by /graph-data endpoint.
        """
        self.model.compute_influence()
        self.model.compute_communities()
        graph_data = self.visualizer.build_graph_data(self.model)
        return {
            "graph": graph_data,
            "physicsConfig": self.visualizer.config,
        }

    # ---------- Node operations ----------

    def add_or_update_node_from_payload(self, payload: Dict[str, Any]) -> None:
        node_id = (payload.get("id") or payload.get("name") or "").strip()
        if not node_id:
            raise ValueError("Node id/name is required")

        node = Node(
            id=node_id,
            label=payload.get("label") or node_id,
            category=payload.get("category"),
            valuation=self._safe_float(payload.get("valuation")),
            role=payload.get("role"),
            company_type=payload.get("company_type"),
            logo_url=payload.get("logo_url"),
            metadata=payload.get("metadata") or {},
        )
        self.model.add_or_update_node(node)
        self._persist()

    def delete_node(self, node_id: str) -> None:
        self.model.delete_node(node_id)
        self._persist()

    def rename_node(self, node_id: str, new_id: str, new_label: Optional[str]) -> None:
        self.model.rename_node(node_id, new_id, new_label)
        self._persist()

    # ---------- Edge operations ----------

    def add_or_update_edge_from_payload(self, payload: Dict[str, Any]) -> None:
        source = (payload.get("source") or "").strip()
        target = (payload.get("target") or "").strip()
        if not source or not target:
            raise ValueError("Both source and target are required")

        relationship_type = (payload.get("relationship_type") or "unknown").strip()
        impact = self._safe_float(payload.get("impact"), default=0.5)
        if impact is None:
            impact = 0.5

        self.model.add_or_update_edge(
            source=source,
            target=target,
            relationship_type=relationship_type,
            impact=impact,
            metadata=payload.get("metadata") or {},
            directed=True,
        )
        self._persist()

    def delete_edge(self, source: str, target: str, relationship_type: Optional[str]) -> None:
        self.model.delete_edge(source, target, relationship_type)
        self._persist()

    # ---------- Analytics / actions ----------

    def run_community_detection(self) -> None:
        self.model.compute_communities()
        self._persist()

    def reload_from_disk(self, path) -> None:
        self.model = self.io_module.load_graph(path)
        # no persist here – just reload

    def save_to_disk(self, path) -> None:
        self.io_module.save_graph(self.model, path)

    # ---------- Helpers ----------

    def _persist(self) -> None:
        self.io_module.save_graph(self.model, self.io_module.DEFAULT_PATH)

    @staticmethod
    def _safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
        if value is None or value == "":
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
