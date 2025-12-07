from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Node:
    """
    Logical node wrapper.

    This holds business-level metadata. The GraphModel stores `Node`
    on the underlying NetworkX graph as node attributes.
    """
    id: str
    label: Optional[str] = None
    category: Optional[str] = None
    valuation: Optional[float] = None
    role: Optional[str] = None
    company_type: Optional[str] = None
    logo_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
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
