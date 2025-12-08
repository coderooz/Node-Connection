"""
Flask routes and endpoint definitions.
"""
from typing import Any
from flask import Blueprint, Flask, jsonify, render_template, request

from .controllers import AppController
from visualization.network_visualizer import NetworkVisualizer
from utils.validators import ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
bp = Blueprint("main", __name__)

# Global controller reference (set during init)
_controller: AppController = None


def init_routes(app: Flask, controller: AppController, 
                visualizer: NetworkVisualizer) -> None:
    """
    Initialize routes with controller instance.
    
    Args:
        app: Flask application
        controller: Application controller
        visualizer: Network visualizer (unused but kept for compatibility)
    """
    global _controller
    _controller = controller
    app.register_blueprint(bp)
    logger.info("Routes initialized")


# ========== Web Interface ==========

@bp.route("/")
def index() -> Any:
    """Render main application page."""
    return render_template("index.html")


@bp.route("/health")
def health() -> Any:
    """Health check endpoint."""
    nodes, edges = _controller.model.summary()
    return jsonify({
        "status": "ok",
        "nodes": nodes,
        "edges": edges
    })


# ========== Graph Data ==========

@bp.route("/graph-data")
def graph_data() -> Any:
    """Get complete graph data for visualization."""
    try:
        payload = _controller.get_graph_payload()
        return jsonify(payload)
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        return jsonify({"error": str(e)}), 500


# ========== Node Operations ==========

@bp.route("/api/nodes/add", methods=["POST"])
def api_nodes_add() -> Any:
    """Add or update a node."""
    try:
        data = request.get_json() or {}
        _controller.add_or_update_node(data)
        return jsonify({"status": "ok", "message": "Node saved successfully"})
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding node: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/nodes/delete", methods=["POST"])
def api_nodes_delete() -> Any:
    """Delete a node."""
    try:
        data = request.get_json() or {}
        node_id = data.get("id")
        if not node_id:
            return jsonify({"status": "error", "message": "Node ID required"}), 400
        
        _controller.delete_node(node_id)
        return jsonify({"status": "ok", "message": "Node deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting node: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/nodes/list", methods=["GET"])
def api_nodes_list() -> Any:
    """Get list of all nodes."""
    try:
        nodes = _controller.model.get_all_nodes()
        node_list = [
            {
                "id": node.id,
                "label": node.label,
                "category": node.category
            }
            for node in nodes
        ]
        return jsonify({"status": "ok", "nodes": node_list})
    except Exception as e:
        logger.error(f"Error listing nodes: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ========== Edge Operations ==========

@bp.route("/api/edges/add", methods=["POST"])
def api_edges_add() -> Any:
    """Add or update an edge."""
    try:
        data = request.get_json() or {}
        _controller.add_or_update_edge(data)
        return jsonify({"status": "ok", "message": "Edge saved successfully"})
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding edge: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/edges/delete", methods=["POST"])
def api_edges_delete() -> Any:
    """Delete an edge."""
    try:
        data = request.get_json() or {}
        source = data.get("source")
        target = data.get("target")
        relationship_type = data.get("relationship_type")
        
        if not source or not target:
            return jsonify({
                "status": "error",
                "message": "Source and target required"
            }), 400
        
        _controller.delete_edge(source, target, relationship_type)
        return jsonify({"status": "ok", "message": "Edge deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting edge: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ========== Analytics ==========

@bp.route("/api/graph/community", methods=["POST"])
def api_graph_community() -> Any:
    """Run community detection."""
    try:
        _controller.run_community_detection()
        return jsonify({"status": "ok", "message": "Communities detected"})
    except Exception as e:
        logger.error(f"Error in community detection: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/graph/analytics", methods=["POST"])
def api_graph_analytics() -> Any:
    """Recompute all analytics."""
    try:
        _controller.recompute_analytics()
        return jsonify({"status": "ok", "message": "Analytics recomputed"})
    except Exception as e:
        logger.error(f"Error recomputing analytics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ========== Persistence ==========

@bp.route("/api/graph/reload", methods=["POST"])
def api_graph_reload() -> Any:
    """Reload graph from disk."""
    try:
        _controller.reload_from_disk()
        return jsonify({"status": "ok", "message": "Graph reloaded from disk"})
    except Exception as e:
        logger.error(f"Error reloading graph: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/graph/save", methods=["POST"])
def api_graph_save() -> Any:
    """Save graph to disk."""
    try:
        _controller.save_to_disk()
        return jsonify({"status": "ok", "message": "Graph saved to disk"})
    except Exception as e:
        logger.error(f"Error saving graph: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ========== Error Handlers ==========

@bp.errorhandler(404)
def not_found(error) -> Any:
    """Handle 404 errors."""
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@bp.errorhandler(500)
def internal_error(error) -> Any:
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"status": "error", "message": "Internal server error"}), 500