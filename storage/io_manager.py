"""
Graph persistence - loading and saving.
"""
import json
from pathlib import Path
from typing import Dict, Any

from core.graph_model import GraphModel
from core.node import Node
from utils.logger import get_logger

logger = get_logger(__name__)


def load_graph(path: Path) -> GraphModel:
    """
    Load graph from JSON file.
    
    Args:
        path: Path to JSON file
        
    Returns:
        GraphModel instance
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is invalid JSON
    """
    if not path.exists():
        raise FileNotFoundError(f"Graph file not found: {path}")
    
    logger.info(f"Loading graph from {path}")
    
    with path.open("r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
    
    model = GraphModel.from_json(data)
    logger.info(f"Loaded graph: {model.summary()}")
    
    return model


def save_graph(model: GraphModel, path: Path) -> None:
    """
    Save graph to JSON file.
    
    Args:
        model: GraphModel to save
        path: Output path
    """
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Export to JSON
    data = model.to_json()
    
    # Write to file
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved graph to {path}: {model.summary()}")


def load_or_init_graph(path: Path) -> GraphModel:
    """
    Load graph from file, or create demo graph if file doesn't exist.
    
    Args:
        path: Path to JSON file
        
    Returns:
        GraphModel instance
    """
    if path.exists():
        try:
            return load_graph(path)
        except Exception as e:
            logger.error(f"Error loading graph from {path}: {e}")
            logger.info("Creating demo graph instead")
    
    # Create and save demo graph
    model = create_demo_graph()
    save_graph(model, path)
    return model


def create_demo_graph() -> GraphModel:
    """
    Create a demo network graph with sample companies.
    
    Returns:
        GraphModel with demo data
    """
    logger.info("Creating demo graph")
    
    gm = GraphModel()
    
    # Define companies
    companies = [
        Node(
            id="OpenAI",
            label="OpenAI",
            category="AI Lab",
            valuation=80_000_000_000,
            role="Model provider",
            company_type="Private",
            metadata={"location": "San Francisco"},
        ),
        Node(
            id="Nvidia",
            label="Nvidia",
            category="GPU Hardware",
            valuation=2_500_000_000_000,
            role="GPU vendor",
            company_type="Public",
            metadata={"ticker": "NVDA"},
        ),
        Node(
            id="Microsoft",
            label="Microsoft",
            category="Cloud & Software",
            valuation=3_100_000_000_000,
            role="Cloud provider / Investor",
            company_type="Public",
            metadata={"ticker": "MSFT"},
        ),
        Node(
            id="Oracle",
            label="Oracle",
            category="Cloud",
            valuation=300_000_000_000,
            role="Cloud provider",
            company_type="Public",
            metadata={"ticker": "ORCL"},
        ),
        Node(
            id="AMD",
            label="AMD",
            category="GPU Hardware",
            valuation=300_000_000_000,
            role="GPU vendor",
            company_type="Public",
            metadata={"ticker": "AMD"},
        ),
        Node(
            id="Intel",
            label="Intel",
            category="CPU / Foundry",
            valuation=200_000_000_000,
            role="CPU / Foundry",
            company_type="Public",
            metadata={"ticker": "INTC"},
        ),
        Node(
            id="xAI",
            label="xAI",
            category="AI Lab",
            valuation=24_000_000_000,
            role="Model provider",
            company_type="Private",
        ),
        Node(
            id="CoreWeave",
            label="CoreWeave",
            category="AI Cloud",
            valuation=19_000_000_000,
            role="GPU cloud",
            company_type="Private",
        ),
        Node(
            id="Mistral",
            label="Mistral AI",
            category="AI Lab",
            valuation=6_000_000_000,
            role="Model provider",
            company_type="Startup",
        ),
        Node(
            id="FigureAI",
            label="Figure AI",
            category="Robotics",
            valuation=2_600_000_000,
            role="Humanoid robots",
            company_type="Startup",
        ),
        Node(
            id="Anthropic",
            label="Anthropic",
            category="AI Lab",
            valuation=15_000_000_000,
            role="Model provider",
            company_type="Private",
        ),
        Node(
            id="Google",
            label="Google",
            category="Cloud & AI",
            valuation=2_000_000_000_000,
            role="Cloud + AI",
            company_type="Public",
        ),
        Node(
            id="Amazon",
            label="Amazon",
            category="Cloud",
            valuation=1_900_000_000_000,
            role="Cloud provider",
            company_type="Public",
        ),
    ]
    
    # Add nodes
    for company in companies:
        gm.add_or_update_node(company)
    
    # Define relationships
    add = gm.add_or_update_edge
    
    # Hardware supply relationships
    add("Nvidia", "OpenAI", "hardware", 0.85, {"note": "GPU supply"})
    add("Nvidia", "CoreWeave", "hardware", 0.8)
    add("Nvidia", "Microsoft", "hardware", 0.7)
    add("Nvidia", "Amazon", "hardware", 0.7)
    add("Nvidia", "Google", "hardware", 0.7)
    add("Nvidia", "xAI", "hardware", 0.8)
    add("Nvidia", "Mistral", "hardware", 0.6)
    
    add("AMD", "CoreWeave", "hardware", 0.5)
    add("AMD", "Microsoft", "hardware", 0.4)
    add("Intel", "Microsoft", "hardware", 0.2)
    add("Intel", "Amazon", "hardware", 0.2)
    
    # Cloud relationships
    add("Microsoft", "OpenAI", "cloud", 0.9, {"note": "Azure supercomputing"})
    add("Oracle", "OpenAI", "cloud", 0.6, {"note": "OCI for training"})
    add("CoreWeave", "OpenAI", "cloud", 0.7, {"note": "Specialized GPU cloud"})
    add("Mistral", "CoreWeave", "cloud", 0.5)
    add("Anthropic", "Amazon", "cloud", 0.8)
    add("Anthropic", "Google", "cloud", 0.6)
    
    # Investment relationships
    add("Microsoft", "FigureAI", "investment", 0.7)
    add("Google", "Anthropic", "investment", 0.7)
    add("Amazon", "Anthropic", "investment", 0.7)
    
    # Software/Services
    add("OpenAI", "FigureAI", "software", 0.6, {"note": "Models for robotics"})
    add("xAI", "Nvidia", "services", 0.4, {"note": "Model customer"})
    
    # Compute analytics
    gm.compute_influence()
    gm.compute_communities()
    
    logger.info(f"Created demo graph: {gm.summary()}")
    
    return gm