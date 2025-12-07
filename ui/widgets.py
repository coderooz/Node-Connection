from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, render_template, request

from ui.controller import AppController
from visualization.network_visualizer import NetworkVisualizer

bp = Blueprint("main", __name__)

_controller: AppController | None = None
_visualizer: NetworkVisualizer | None = None


def init_app(app, controller: AppController, visualizer: NetworkVisualizer) -> None:
    global _controller, _visualizer
    _controller = controller
    _visualizer = visualizer
    app.register_blueprint(bp)



# ---------- Routes ----------


@bp.route("/")
def index() -> Any:
    return render_template("index.html")


@bp.route("/graph-data")
def graph_data() -> Any:
    payload = _controller.get_graph_payload()
    return jsonify(payload)


@bp.route("/api/nodes/add", methods=["POST"])
def api_nodes_add() -> Any:
    data = request.get_json() or {}
    _controller.add_or_update_node_from_payload(data)
    return jsonify({"status": "ok"})


@bp.route("/api/nodes/delete", methods=["POST"])
def api_nodes_delete() -> Any:
    data = request.get_json() or {}
    node_id = data.get("id")
    if node_id:
        _controller.delete_node(node_id)
    return jsonify({"status": "ok"})


@bp.route("/api/edges/add", methods=["POST"])
def api_edges_add() -> Any:
    data = request.get_json() or {}
    _controller.add_or_update_edge_from_payload(data)
    return jsonify({"status": "ok"})


@bp.route("/api/edges/delete", methods=["POST"])
def api_edges_delete() -> Any:
    data = request.get_json() or {}
    source = data.get("source")
    target = data.get("target")
    relationship_type = data.get("relationship_type")
    if source and target:
        _controller.delete_edge(source, target, relationship_type)
    return jsonify({"status": "ok"})


@bp.route("/api/graph/community", methods=["POST"])
def api_graph_community() -> Any:
    _controller.run_community_detection()
    return jsonify({"status": "ok"})


@bp.route("/api/graph/reload", methods=["POST"])
def api_graph_reload() -> Any:
    _controller.reload_from_disk(io_manager.DEFAULT_PATH)
    return jsonify({"status": "ok"})


@bp.route("/api/graph/save", methods=["POST"])
def api_graph_save() -> Any:
    _controller.save_to_disk(io_manager.DEFAULT_PATH)
    return jsonify({"status": "ok"})


# We import here to avoid circular at module-import time
from storage import io_manager  # noqa: E402  (keep at bottom)
