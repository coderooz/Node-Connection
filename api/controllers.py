"""
Application controller - business logic for API endpoints.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

from core.graph_model import GraphModel
from core.node import Node
from visualization.network_visualizer import NetworkVisualizer
from storage.io_manager import save_graph, load_graph
from utils.validators import validate_node_data, validate_edge_data, ValidationError
from utils.logger import get_logger
import config

logger = get_logger(__name__)


class AppController:
    """
    Application controller coordinating graph model and visualization.
    
    Handles all business logic for API endpoints.
    """
    
    def __init__(
        self,
        graph_model: GraphModel,
        visualizer: NetworkVisualizer,
    ) -> None:
        """
        Initialize controller.
        
        Args:
            graph_model: Graph data model
            visualizer: Visualization data builder
        """
        self.model = graph_model
        self.visualizer = visualizer
    
    # ========== Graph Data ==========
    
    def get_graph_payload(self) -> Dict[str, Any]:
        """
        Get complete graph data for visualization.
        
        Computes analytics and builds visualization-ready data.
        
        Returns:
            Dictionary with graph data and physics config
        """
        # Compute analytics
        self.model.compute_influence()
        self.model.compute_communities()
        
        # Build visualization data
        graph_data = self.visualizer.build_graph_data(self.model)
        
        return {
            "graph": graph_data,
            "physicsConfig": self.visualizer.config,
        }
    
    # ========== Node Operations ==========
    
    def add_or_update_node(self, payload: Dict[str, Any]) -> None:
        """
        Add or update a node from request payload.
        
        Args:
            payload: Request data
            
        Raises:
            ValidationError: If data is invalid
        """
        # Validate input
        is_valid, error_msg = validate_node_data(payload)
        if not is_valid:
            raise ValidationError(error_msg)
        
        # Extract and clean data
        node_id = (payload.get("id") or payload.get("name") or "").strip()
        
        node = Node(
            id=node_id,
            label=payload.get("label") or node_id,
            category=self._clean_string(payload.get("category")),
            valuation=self._safe_float(payload.get("valuation")),
            role=self._clean_string(payload.get("role")),
            company_type=self._clean_string(payload.get("company_type")),
            logo_url=self._clean_string(payload.get("logo_url")),
            metadata=payload.get("metadata") or {},
        )
        
        self.model.add_or_update_node(node)
        self._persist()
        
        logger.info(f"Added/updated node: {node_id}")
    
    def delete_node(self, node_id: str) -> None:
        """
        Delete a node.
        
        Args:
            node_id: ID of node to delete
        """
        success = self.model.delete_node(node_id)
        if success:
            self._persist()
            logger.info(f"Deleted node: {node_id}")
        else:
            logger.warning(f"Node not found for deletion: {node_id}")
    
    def rename_node(self, node_id: str, new_id: str, 
                    new_label: Optional[str] = None) -> None:
        """
        Rename a node.
        
        Args:
            node_id: Current ID
            new_id: New ID
            new_label: Optional new label
        """
        self.model.rename_node(node_id, new_id, new_label)
        self._persist()
        logger.info(f"Renamed node: {node_id} -> {new_id}")
    
    # ========== Edge Operations ==========
    
    def add_or_update_edge(self, payload: Dict[str, Any]) -> None:
        """
        Add or update an edge from request payload.
        
        Args:
            payload: Request data
            
        Raises:
            ValidationError: If data is invalid
        """
        # Validate input
        is_valid, error_msg = validate_edge_data(payload)
        if not is_valid:
            raise ValidationError(error_msg)
        
        # Extract data
        source = (payload.get("source") or "").strip()
        target = (payload.get("target") or "").strip()
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
        logger.info(f"Added/updated edge: {source} -> {target}")
    
    def delete_edge(self, source: str, target: str, 
                    relationship_type: Optional[str] = None) -> None:
        """
        Delete an edge.
        
        Args:
            source: Source node ID
            target: Target node ID
            relationship_type: Optional relationship type filter
        """
        success = self.model.delete_edge(source, target, relationship_type)
        if success:
            self._persist()
            logger.info(f"Deleted edge: {source} -> {target}")
        else:
            logger.warning(f"Edge not found for deletion: {source} -> {target}")
    
    # ========== Analytics ==========
    
    def run_community_detection(self) -> None:
        """Run community detection algorithm."""
        self.model.compute_communities()
        self._persist()
        logger.info("Ran community detection")
    
    def recompute_analytics(self) -> None:
        """Recompute all analytics (influence and communities)."""
        self.model.compute_influence()
        self.model.compute_communities()
        self._persist()
        logger.info("Recomputed analytics")
    
    # ========== Persistence ==========
    
    def reload_from_disk(self) -> None:
        """Reload graph from disk, discarding changes."""
        self.model = load_graph(config.DEFAULT_NETWORK_FILE)
        logger.info("Reloaded graph from disk")
    
    def save_to_disk(self) -> None:
        """Save current graph to disk."""
        save_graph(self.model, config.DEFAULT_NETWORK_FILE)
        logger.info("Saved graph to disk")
    
    def _persist(self) -> None:
        """Persist graph after changes."""
        save_graph(self.model, config.DEFAULT_NETWORK_FILE)
    
    # ========== Utilities ==========
    
    @staticmethod
    def _clean_string(value: Any) -> Optional[str]:
        """Clean and validate string input."""
        if value is None or value == "":
            return None
        result = str(value).strip()
        return result if result else None
    
    @staticmethod
    def _safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
        """Safely convert value to float."""
        if value is None or value == "":
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default