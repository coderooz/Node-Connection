"""
Graph data model with analytics capabilities.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Set
import networkx as nx

from .node import Node
from .analytics import compute_influence, compute_communities
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphModel:
    """
    Core graph data model with network analysis capabilities.
    
    Manages nodes, edges, and provides analytics functions like
    centrality calculations and community detection.
    """
    
    def __init__(self) -> None:
        """Initialize empty directed graph."""
        self.graph: nx.DiGraph = nx.DiGraph()
        self._analytics_cache: Dict[str, Any] = {}
        self._cache_valid = False
    
    # ========== Node Operations ==========
    
    def add_or_update_node(self, node: Node) -> None:
        """
        Add a new node or update existing node.
        
        Args:
            node: Node instance to add/update
        """
        attrs = node.to_dict()
        self.graph.add_node(node.id, node=node, **attrs)
        self._invalidate_cache()
        logger.debug(f"Added/updated node: {node.id}")
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all its edges.
        
        Args:
            node_id: ID of node to delete
            
        Returns:
            True if node was deleted, False if not found
        """
        if node_id in self.graph:
            self.graph.remove_node(node_id)
            self._invalidate_cache()
            logger.debug(f"Deleted node: {node_id}")
            return True
        return False
    
    def rename_node(self, node_id: str, new_id: str, 
                    new_label: Optional[str] = None) -> None:
        """
        Rename a node (change its ID).
        
        Args:
            node_id: Current node ID
            new_id: New node ID
            new_label: Optional new label
            
        Raises:
            ValueError: If node not found or new_id already exists
        """
        if node_id not in self.graph:
            raise ValueError(f"Node '{node_id}' not found")
        
        if new_id != node_id and new_id in self.graph:
            raise ValueError(f"Node ID '{new_id}' already exists")
        
        # Get current data
        data = self.graph.nodes[node_id].copy()
        node_obj: Optional[Node] = data.get("node")
        
        # Update node object
        if node_obj:
            node_obj.id = new_id
            if new_label:
                node_obj.label = new_label
        
        # Update attributes
        data["id"] = new_id
        if new_label:
            data["label"] = new_label
        
        # Relabel in graph
        nx.relabel_nodes(self.graph, {node_id: new_id}, copy=False)
        self.graph.nodes[new_id].update(data)
        
        self._invalidate_cache()
        logger.debug(f"Renamed node: {node_id} -> {new_id}")
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get node by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node instance or None if not found
        """
        data = self.graph.nodes.get(node_id)
        if not data:
            return None
        return data.get("node")
    
    def get_all_nodes(self) -> List[Node]:
        """Get all nodes in the graph."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            node = data.get("node")
            if node:
                nodes.append(node)
        return nodes
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """
        Get all neighbors (predecessors and successors) of a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            List of neighbor node IDs
        """
        if node_id not in self.graph:
            return []
        
        predecessors = list(self.graph.predecessors(node_id))
        successors = list(self.graph.successors(node_id))
        
        # Combine and remove duplicates
        neighbors = list(set(predecessors + successors))
        return neighbors
    
    # ========== Edge Operations ==========
    
    def add_or_update_edge(
        self,
        source: str,
        target: str,
        relationship_type: str = "unknown",
        impact: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
        directed: bool = True,
    ) -> None:
        """
        Add or update an edge between nodes.
        
        Args:
            source: Source node ID
            target: Target node ID
            relationship_type: Type of relationship
            impact: Impact/strength (0.0-1.0)
            metadata: Additional edge data
            directed: Whether edge is directed
        """
        # Ensure nodes exist
        if source not in self.graph:
            self.add_or_update_node(Node(id=source, label=source))
        if target not in self.graph:
            self.add_or_update_node(Node(id=target, label=target))
        
        # Clamp impact to valid range
        impact = max(0.0, min(1.0, float(impact)))
        
        # Edge attributes
        attrs = {
            "relationship_type": relationship_type or "unknown",
            "impact": impact,
            "directed": directed,
            "metadata": metadata or {},
        }
        
        self.graph.add_edge(source, target, **attrs)
        self._invalidate_cache()
        logger.debug(f"Added edge: {source} -> {target} ({relationship_type})")
    
    def delete_edge(self, source: str, target: str, 
                    relationship_type: Optional[str] = None) -> bool:
        """
        Delete an edge.
        
        Args:
            source: Source node ID
            target: Target node ID
            relationship_type: If specified, only delete if type matches
            
        Returns:
            True if edge was deleted, False if not found
        """
        if not self.graph.has_edge(source, target):
            return False
        
        # Check relationship type if specified
        if relationship_type is not None:
            data = self.graph.get_edge_data(source, target)
            if data and data.get("relationship_type") != relationship_type:
                return False
        
        self.graph.remove_edge(source, target)
        self._invalidate_cache()
        logger.debug(f"Deleted edge: {source} -> {target}")
        return True
    
    def get_edge(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        if self.graph.has_edge(source, target):
            return self.graph.get_edge_data(source, target)
        return None
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Get all edges with their data."""
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edge = data.copy()
            edge['source'] = u
            edge['target'] = v
            edges.append(edge)
        return edges
    
    # ========== Analytics ==========
    
    def compute_influence(self) -> None:
        """
        Compute influence scores for all nodes.
        Uses eigenvector centrality with fallback to degree centrality.
        """
        if self.graph.number_of_nodes() == 0:
            return
        
        influence_scores = compute_influence(self.graph)
        
        # Store in node attributes
        for node_id, score in influence_scores.items():
            if node_id in self.graph:
                self.graph.nodes[node_id]["influence"] = score
        
        self._analytics_cache["influence"] = influence_scores
        logger.info(f"Computed influence for {len(influence_scores)} nodes")
    
    def compute_communities(self) -> None:
        """
        Detect communities using modularity-based clustering.
        """
        if self.graph.number_of_nodes() == 0:
            return
        
        communities = compute_communities(self.graph)
        
        # Store in node attributes
        for node_id, community_id in communities.items():
            if node_id in self.graph:
                self.graph.nodes[node_id]["community"] = community_id
        
        self._analytics_cache["communities"] = communities
        logger.info(f"Detected {len(set(communities.values()))} communities")
    
    def get_node_influence(self, node_id: str) -> float:
        """Get influence score for a node."""
        if node_id not in self.graph:
            return 0.0
        return self.graph.nodes[node_id].get("influence", 0.0)
    
    def get_node_community(self, node_id: str) -> Optional[int]:
        """Get community ID for a node."""
        if node_id not in self.graph:
            return None
        return self.graph.nodes[node_id].get("community")
    
    def get_top_influential_nodes(self, n: int = 10) -> List[Tuple[str, float]]:
        """
        Get top N most influential nodes.
        
        Args:
            n: Number of nodes to return
            
        Returns:
            List of (node_id, influence_score) tuples
        """
        if "influence" not in self._analytics_cache:
            self.compute_influence()
        
        scores = self._analytics_cache.get("influence", {})
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:n]
    
    # ========== Serialization ==========
    
    def to_json(self) -> Dict[str, Any]:
        """
        Export graph to JSON-serializable format.
        
        Returns:
            Dictionary with nodes and edges
        """
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            node_obj: Optional[Node] = data.get("node")
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
            
            # Add analytics data
            base["influence"] = data.get("influence", 0.0)
            base["community"] = data.get("community")
            nodes.append(base)
        
        edges = []
        for u, v, edata in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relationship_type": edata.get("relationship_type", "unknown"),
                "impact": edata.get("impact", 0.5),
                "directed": edata.get("directed", True),
                "metadata": edata.get("metadata", {}),
            })
        
        return {
            "version": 1,
            "nodes": nodes,
            "edges": edges,
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> GraphModel:
        """
        Create graph from JSON data.
        
        Args:
            data: Dictionary with nodes and edges
            
        Returns:
            New GraphModel instance
        """
        model = cls()
        
        # Add nodes
        for node_data in data.get("nodes", []):
            node = Node.from_dict(node_data)
            model.add_or_update_node(node)
            
            # Restore analytics if present
            node_id = node.id
            if "influence" in node_data:
                model.graph.nodes[node_id]["influence"] = node_data["influence"]
            if "community" in node_data:
                model.graph.nodes[node_id]["community"] = node_data["community"]
        
        # Add edges
        for edge_data in data.get("edges", []):
            model.add_or_update_edge(
                source=edge_data["source"],
                target=edge_data["target"],
                relationship_type=edge_data.get("relationship_type", "unknown"),
                impact=edge_data.get("impact", 0.5),
                metadata=edge_data.get("metadata"),
                directed=edge_data.get("directed", True),
            )
        
        logger.info(f"Loaded graph from JSON: {model.summary()}")
        return model
    
    # ========== Utilities ==========
    
    def summary(self) -> Tuple[int, int]:
        """
        Get graph summary.
        
        Returns:
            Tuple of (num_nodes, num_edges)
        """
        return self.graph.number_of_nodes(), self.graph.number_of_edges()
    
    def clear(self) -> None:
        """Clear all nodes and edges."""
        self.graph.clear()
        self._invalidate_cache()
        logger.info("Cleared graph")
    
    def _invalidate_cache(self) -> None:
        """Invalidate analytics cache."""
        self._cache_valid = False
        self._analytics_cache.clear()
    
    def __repr__(self) -> str:
        """String representation."""
        n_nodes, n_edges = self.summary()
        return f"GraphModel(nodes={n_nodes}, edges={n_edges})"