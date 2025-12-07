from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from model import GraphModel, Node

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PATH = BASE_DIR / "storage" / "default_network.json"


def load_graph(path: Path) -> GraphModel:
    if not path.exists():
        return GraphModel()
    with path.open("r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
    return GraphModel.from_json(data)


def save_graph(model: GraphModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = model.to_json()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_or_init_graph(path: Path) -> GraphModel:
    if path.exists():
        return load_graph(path)
    model = create_demo_graph()
    save_graph(model, path)
    return model


def create_demo_graph() -> GraphModel:
    """
    Seed graph with demo company relationships:
    OpenAI, Nvidia, Microsoft, Oracle, AMD, Intel, xAI, CoreWeave, Mistral, Figure AI, etc.
    """
    gm = GraphModel()

    # Nodes
    companies = [
        Node(
            id="OpenAI",
            label="OpenAI",
            category="AI Lab",
            valuation=80000000000,
            role="Model provider",
            company_type="Private",
            metadata={"location": "San Francisco"},
        ),
        Node(
            id="Nvidia",
            label="Nvidia",
            category="GPU Hardware",
            valuation=2500000000000,
            role="GPU vendor",
            company_type="Public",
            metadata={"ticker": "NVDA"},
        ),
        Node(
            id="Microsoft",
            label="Microsoft",
            category="Cloud & Software",
            valuation=3100000000000,
            role="Cloud provider / Investor",
            company_type="Public",
            metadata={"ticker": "MSFT"},
        ),
        Node(
            id="Oracle",
            label="Oracle",
            category="Cloud",
            valuation=300000000000,
            role="Cloud provider",
            company_type="Public",
            metadata={"ticker": "ORCL"},
        ),
        Node(
            id="AMD",
            label="AMD",
            category="GPU Hardware",
            valuation=300000000000,
            role="GPU vendor",
            company_type="Public",
            metadata={"ticker": "AMD"},
        ),
        Node(
            id="Intel",
            label="Intel",
            category="CPU / Foundry",
            valuation=200000000000,
            role="CPU / Foundry",
            company_type="Public",
            metadata={"ticker": "INTC"},
        ),
        Node(
            id="xAI",
            label="xAI",
            category="AI Lab",
            valuation=24000000000,
            role="Model provider",
            company_type="Private",
        ),
        Node(
            id="CoreWeave",
            label="CoreWeave",
            category="AI Cloud",
            valuation=19000000000,
            role="GPU cloud",
            company_type="Private",
        ),
        Node(
            id="Mistral",
            label="Mistral AI",
            category="AI Lab",
            valuation=6000000000,
            role="Model provider",
            company_type="Startup",
        ),
        Node(
            id="FigureAI",
            label="Figure AI",
            category="Robotics",
            valuation=2600000000,
            role="Humanoid robots",
            company_type="Startup",
        ),
        Node(
            id="Anthropic",
            label="Anthropic",
            category="AI Lab",
            valuation=15000000000,
            role="Model provider",
            company_type="Private",
        ),
        Node(
            id="Google",
            label="Google",
            category="Cloud & AI",
            valuation=2000000000000,
            role="Cloud + AI",
            company_type="Public",
        ),
        Node(
            id="Amazon",
            label="Amazon",
            category="Cloud",
            valuation=1900000000000,
            role="Cloud provider",
            company_type="Public",
        ),
    ]

    for node in companies:
        gm.add_or_update_node(node)

    # Edges (relationships)
    add = gm.add_or_update_edge

    # Investment & partnership edges
    add("Microsoft", "OpenAI", "investment", 0.95, {"note": "Strategic partnership"})
    add("Microsoft", "OpenAI", "cloud", 0.9, {"note": "Azure supercomputing"})
    add("Nvidia", "OpenAI", "hardware", 0.85, {"note": "GPU supply"})
    add("Oracle", "OpenAI", "cloud", 0.6, {"note": "OCI for training"})
    add("CoreWeave", "OpenAI", "cloud", 0.7, {"note": "Specialized GPU cloud"})

    add("Nvidia", "CoreWeave", "hardware", 0.8)
    add("Nvidia", "Microsoft", "hardware", 0.7)
    add("Nvidia", "Amazon", "hardware", 0.7)
    add("Nvidia", "Google", "hardware", 0.7)

    add("Microsoft", "FigureAI", "investment", 0.7)
    add("OpenAI", "FigureAI", "software", 0.6, {"note": "Models for robotics"})

    add("Google", "Anthropic", "investment", 0.7)
    add("Amazon", "Anthropic", "investment", 0.7)
    add("Anthropic", "Amazon", "cloud", 0.8)
    add("Anthropic", "Google", "cloud", 0.6)

    add("Nvidia", "xAI", "hardware", 0.8)
    add("xAI", "Nvidia", "services", 0.4, {"note": "Model customer"})

    add("Nvidia", "Mistral", "hardware", 0.6)
    add("Mistral", "CoreWeave", "cloud", 0.5)

    add("AMD", "CoreWeave", "hardware", 0.5)
    add("AMD", "Microsoft", "hardware", 0.4)
    add("Intel", "Microsoft", "hardware", 0.2)
    add("Intel", "Amazon", "hardware", 0.2)

    gm.compute_influence()
    gm.compute_communities()
    return gm
