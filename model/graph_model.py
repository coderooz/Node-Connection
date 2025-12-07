from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import networkx as nx
from .node import Node


class GraphModel:
    """
    Core graph data model.

    - Manages nodes and edges
    - Computes influence (centrality)
    - Computes communities (for clustering)
    - Provides serialization to/from JSON
    """

    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()

    # ---------- Node operations ----------

    def add_or_update_node(self, node: Node) -> None:
        """
        Add a new node or update an existing one.
        """
        attrs = node.to_dict()
        self.graph.add_node(node.id, node=node, **attrs)

    def delete_node(self, node_id: str) -> None:
        if node_id in self.graph:
            self.graph.remove_node(node_id)

    def rename_node(self, node_id: str, new_id: str, new_label: Optional[str] = None) -> None:
        if node_id not in self.graph:
            return

        if new_id in self.graph and new_id != node_id:
            raise ValueError(f"Cannot rename {node_id}: target id {new_id} already exists")

        data = self.graph.nodes[node_id].copy()

        node_obj: Optional[Node] = data.get("node")
        if node_obj:
            node_obj.id = new_id
            if new_label:
                node_obj.label = new_label

        data["id"] = new_id
        if new_label:
            data["label"] = new_label

        # Rebuild graph with renamed node
        nx.relabel_nodes(self.graph, {node_id: new_id}, copy=False)
        self.graph.nodes[new_id].update(data)

    def get_node(self, node_id: str) -> Optional[Node]:
        data = self.graph.nodes.get(node_id)
        if not data:
            return None
        return data.get("node")

    def get_neighbors(self, node_id: str) -> List[str]:
        if node_id not in self.graph:
            return []
        return list(self.graph.successors(node_id)) + list(self.graph.predecessors(node_id))

    # ---------- Edge operations ----------

    def add_or_update_edge(
        self,
        source: str,
        target: str,
        relationship_type: str,
        impact: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
        directed: bool = True,
    ) -> None:
        if source not in self.graph:
            self.add_or_update_node(Node(id=source, label=source))
        if target not in self.graph:
            self.add_or_update_node(Node(id=target, label=target))

        impact_clamped = max(0.0, min(1.0, float(impact)))
        attrs = {
            "relationship_type": relationship_type or "unknown",
            "impact": impact_clamped,
            "directed": directed,
            "metadata": metadata or {},
        }
        self.graph.add_edge(source, target, **attrs)

    def delete_edge(self, source: str, target: str, relationship_type: Optional[str] = None) -> None:
        if not self.graph.has_edge(source, target):
            return
        if relationship_type is None:
            self.graph.remove_edge(source, target)
        else:
            data = self.graph.get_edge_data(source, target)
            if data and data.get("relationship_type") == relationship_type:
                self.graph.remove_edge(source, target)

    # ---------- Analytics ----------

    def compute_influence(self) -> None:
        """
        Compute influence for each node.

        Tries eigenvector centrality with impact as weight; falls back to degree centrality.
        """
        if self.graph.number_of_nodes() == 0:
            return

        try:
            # Use impact as edge weight
            influence = nx.eigenvector_centrality_numpy(self.graph, weight="impact")
        except Exception:
            # Fallback: degree centrality
            influence = nx.degree_centrality(self.graph.to_undirected())

        # Normalize to [0, 1]
        max_val = max(influence.values()) if influence else 1.0
        for node_id, value in influence.items():
            norm = float(value) / float(max_val) if max_val else 0.0
            self.graph.nodes[node_id]["influence"] = norm

    def compute_communities(self) -> None:
        """
        Community detection for clustering toggle.

        Uses greedy modularity on the undirected version.
        """
        if self.graph.number_of_nodes() == 0:
            return

        undirected = self.graph.to_undirected()
        communities = list(nx.algorithms.community.greedy_modularity_communities(undirected))
        for idx, community in enumerate(communities):
            for node_id in community:
                self.graph.nodes[node_id]["community"] = idx

    # ---------- Serialization ----------

    def to_json(self) -> Dict[str, Any]:
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

            # Analytics
            base["influence"] = data.get("influence", 0.0)
            base["community"] = data.get("community")
            nodes.append(base)

        edges = []
        for u, v, edata in self.graph.edges(data=True):
            edges.append(
                {
                    "source": u,
                    "target": v,
                    "relationship_type": edata.get("relationship_type"),
                    "impact": edata.get("impact", 0.5),
                    "directed": edata.get("directed", True),
                    "metadata": edata.get("metadata", {}),
                }
            )

        return {
            "version": 1,
            "nodes": nodes,
            "edges": edges,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "GraphModel":
        gm = cls()
        for n in data.get("nodes", []):
            node = Node.from_dict(n)
            gm.add_or_update_node(node)
            # Restore analytics if present
            if "influence" in n:
                gm.graph.nodes[node.id]["influence"] = n["influence"]
            if "community" in n:
                gm.graph.nodes[node.id]["community"] = n["community"]

        for e in data.get("edges", []):
            gm.add_or_update_edge(
                source=e["source"],
                target=e["target"],
                relationship_type=e.get("relationship_type", "unknown"),
                impact=e.get("impact", 0.5),
                metadata=e.get("metadata"),
                directed=e.get("directed", True),
            )
        return gm

    # Convenience

    def summary(self) -> Tuple[int, int]:
        return self.graph.number_of_nodes(), self.graph.number_of_edges()
