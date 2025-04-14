"""
OpenAPI specification loading and utilities for Riksbank APIs.
"""

import json
import os
from typing import Any, Dict

def load_openapi_spec(filename: str) -> Dict[str, Any]:
    """
    Load an OpenAPI specification from a JSON file.
    
    Args:
        filename: Name of the JSON file in the openapi directory
        
    Returns:
        The parsed OpenAPI specification as a dictionary
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(current_dir, filename)
    
    with open(spec_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Pre-load the specifications
MONETARY_POLICY_SPEC = load_openapi_spec('monetary_policy_data.json')
