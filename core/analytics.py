"""
Network analysis algorithms and utilities.
"""
from typing import Dict
import networkx as nx
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_influence(graph: nx.DiGraph) -> Dict[str, float]:
    """
    Compute influence scores using centrality measures.
    
    Tries eigenvector centrality first (with impact weights),
    falls back to degree centrality if that fails.
    
    Args:
        graph: NetworkX directed graph
        
    Returns:
        Dictionary mapping node_id to normalized influence score (0-1)
    """
    if graph.number_of_nodes() == 0:
        return {}
    
    try:
        # Try eigenvector centrality with impact as weight
        influence = nx.eigenvector_centrality_numpy(
            graph, 
            weight="impact",
            max_iter=1000
        )
        logger.debug("Used eigenvector centrality for influence")
    except Exception as e:
        logger.warning(f"Eigenvector centrality failed: {e}. Using degree centrality.")
        # Fallback to degree centrality
        influence = nx.degree_centrality(graph.to_undirected())
    
    # Normalize to [0, 1]
    if not influence:
        return {}
    
    max_val = max(influence.values()) if influence else 1.0
    if max_val == 0:
        max_val = 1.0
    
    normalized = {
        node_id: float(score) / float(max_val)
        for node_id, score in influence.items()
    }
    
    return normalized


def compute_communities(graph: nx.DiGraph) -> Dict[str, int]:
    """
    Detect communities using greedy modularity optimization.
    
    Args:
        graph: NetworkX directed graph
        
    Returns:
        Dictionary mapping node_id to community_id (int)
    """
    if graph.number_of_nodes() == 0:
        return {}
    
    # Convert to undirected for community detection
    undirected = graph.to_undirected()
    
    # Use greedy modularity communities
    communities = list(
        nx.algorithms.community.greedy_modularity_communities(undirected)
    )
    
    # Map nodes to community IDs
    node_to_community = {}
    for idx, community in enumerate(communities):
        for node_id in community:
            node_to_community[node_id] = idx
    
    logger.debug(f"Detected {len(communities)} communities")
    return node_to_community


def compute_betweenness_centrality(graph: nx.DiGraph) -> Dict[str, float]:
    """
    Compute betweenness centrality (how often node is on shortest paths).
    
    Args:
        graph: NetworkX directed graph
        
    Returns:
        Dictionary mapping node_id to betweenness score
    """
    if graph.number_of_nodes() == 0:
        return {}
    
    return nx.betweenness_centrality(graph, weight="impact")


def compute_pagerank(graph: nx.DiGraph) -> Dict[str, float]:
    """
    Compute PageRank scores.
    
    Args:
        graph: NetworkX directed graph
        
    Returns:
        Dictionary mapping node_id to PageRank score
    """
    if graph.number_of_nodes() == 0:
        return {}
    
    return nx.pagerank(graph, weight="impact")


def find_shortest_path(graph: nx.DiGraph, source: str, target: str) -> list:
    """
    Find shortest path between two nodes.
    
    Args:
        graph: NetworkX directed graph
        source: Source node ID
        target: Target node ID
        
    Returns:
        List of node IDs forming the path, or empty list if no path exists
    """
    try:
        return nx.shortest_path(graph, source, target, weight="impact")
    except nx.NetworkXNoPath:
        return []


def detect_cycles(graph: nx.DiGraph) -> list:
    """
    Detect cycles in the graph.
    
    Args:
        graph: NetworkX directed graph
        
    Returns:
        List of cycles (each cycle is a list of node IDs)
    """
    try:
        cycles = list(nx.simple_cycles(graph))
        return cycles
    except Exception as e:
        logger.error(f"Error detecting cycles: {e}")
        return []