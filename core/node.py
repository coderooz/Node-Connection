"""
Node data model representing a network entity.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional


@dataclass
class Node:
    """
    Represents a node in the network graph.
    
    Attributes:
        id: Unique identifier
        label: Display name
        category: Node category/type
        valuation: Numeric value (e.g., company valuation)
        role: Function or role in network
        company_type: Entity type (Public, Private, etc.)
        logo_url: URL to logo/avatar image
        metadata: Additional custom data
    """
    
    id: str
    label: Optional[str] = None
    category: Optional[str] = None
    valuation: Optional[float] = None
    role: Optional[str] = None
    company_type: Optional[str] = None
    logo_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Ensure ID is valid
        if not self.id or not str(self.id).strip():
            raise ValueError("Node ID cannot be empty")
        
        self.id = str(self.id).strip()
        
        # Set default label
        if not self.label:
            self.label = self.id
        
        # Ensure metadata is a dict
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "id": self.id,
            "label": self.label or self.id,
            "category": self.category,
            "valuation": self.valuation,
            "role": self.role,
            "company_type": self.company_type,
            "logo_url": self.logo_url,
            "metadata": self.metadata or {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Node:
        """Create node from dictionary."""
        return cls(
            id=data["id"],
            label=data.get("label"),
            category=data.get("category"),
            valuation=data.get("valuation"),
            role=data.get("role"),
            company_type=data.get("company_type"),
            logo_url=data.get("logo_url"),
            metadata=data.get("metadata") or {},
        )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Node(id='{self.id}', label='{self.label}', category='{self.category}')"
    
    def __hash__(self) -> int:
        """Make node hashable for use in sets."""
        return hash(self.id)
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on ID."""
        if isinstance(other, Node):
            return self.id == other.id
        return False