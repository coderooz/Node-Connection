"""
Input validation utilities.
"""
from typing import Dict, Any, List, Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_node_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate node data.
    
    Returns:
        (is_valid, error_message)
    """
    # Check required fields
    node_id = data.get('id') or data.get('name')
    if not node_id or not str(node_id).strip():
        return False, "Node ID/name is required and cannot be empty"
    
    # Validate ID format
    node_id = str(node_id).strip()
    if len(node_id) > 100:
        return False, "Node ID must be 100 characters or less"
    
    # Validate valuation if provided
    if 'valuation' in data and data['valuation'] is not None:
        try:
            val = float(data['valuation'])
            if val < 0:
                return False, "Valuation cannot be negative"
        except (TypeError, ValueError):
            return False, "Valuation must be a valid number"
    
    return True, None


def validate_edge_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate edge data.
    
    Returns:
        (is_valid, error_message)
    """
    # Check required fields
    source = data.get('source')
    target = data.get('target')
    
    if not source or not str(source).strip():
        return False, "Source node is required"
    
    if not target or not str(target).strip():
        return False, "Target node is required"
    
    # Validate source != target
    if str(source).strip() == str(target).strip():
        return False, "Source and target must be different nodes"
    
    # Validate impact if provided
    if 'impact' in data:
        try:
            impact = float(data['impact'])
            if not (0.0 <= impact <= 1.0):
                return False, "Impact must be between 0.0 and 1.0"
        except (TypeError, ValueError):
            return False, "Impact must be a valid number"
    
    # Validate relationship type
    valid_types = {
        'investment', 'hardware', 'software', 'cloud', 'services',
        'vc', 'research', 'partnership', 'supply', 'other', 'unknown'
    }
    
    rel_type = data.get('relationship_type', '').lower()
    if rel_type and rel_type not in valid_types:
        # Allow custom types but warn
        pass
    
    return True, None


def sanitize_string(value: Any, max_length: int = 200) -> str:
    """Sanitize string input."""
    if value is None:
        return ""
    
    result = str(value).strip()
    if len(result) > max_length:
        result = result[:max_length]
    
    return result


def sanitize_number(value: Any, default: float = 0.0, 
                    min_val: Optional[float] = None,
                    max_val: Optional[float] = None) -> float:
    """Sanitize numeric input."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    
    if min_val is not None and result < min_val:
        result = min_val
    if max_val is not None and result > max_val:
        result = max_val
    
    return result