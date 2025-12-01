"""
WoT Thing Description validator.

This module validates WoT Thing Descriptions against the W3C WoT specification.
"""

from typing import Dict, Any, Tuple, List


def validate_wot_thing_description(wot_td: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a WoT Thing Description.
    
    Checks for required fields and basic structure according to W3C WoT specification.
    
    Args:
        wot_td: Dictionary representing a WoT Thing Description
        
    Returns:
        Tuple of (is_valid, list_of_errors_or_warnings)
        
    References:
        - W3C WoT Thing Description: https://www.w3.org/TR/wot-thing-description/
    """
    errors = []
    warnings = []
    
    # Check required fields
    required_fields = ["@context", "title", "security", "securityDefinitions"]
    for field in required_fields:
        if field not in wot_td:
            errors.append(f"Missing required field: {field}")
    
    # Validate @context
    if "@context" in wot_td:
        context = wot_td["@context"]
        if isinstance(context, str):
            if "wot/td" not in context:
                warnings.append("@context should reference W3C WoT TD context")
        elif isinstance(context, list):
            has_wot_context = any("wot/td" in str(c) for c in context)
            if not has_wot_context:
                warnings.append("@context should include W3C WoT TD context")
    
    # Validate title
    if "title" in wot_td:
        if not isinstance(wot_td["title"], str) or not wot_td["title"]:
            errors.append("title must be a non-empty string")
    
    # Validate security
    if "security" in wot_td:
        if not isinstance(wot_td["security"], (list, str)):
            errors.append("security must be a string or array")
        
        # Check that referenced security schemes exist
        security_refs = wot_td["security"] if isinstance(wot_td["security"], list) else [wot_td["security"]]
        security_defs = wot_td.get("securityDefinitions", {})
        
        for ref in security_refs:
            if ref not in security_defs:
                errors.append(f"Security scheme '{ref}' referenced but not defined in securityDefinitions")
    
    # Validate securityDefinitions
    if "securityDefinitions" in wot_td:
        if not isinstance(wot_td["securityDefinitions"], dict):
            errors.append("securityDefinitions must be an object")
        else:
            for scheme_name, scheme_def in wot_td["securityDefinitions"].items():
                if not isinstance(scheme_def, dict):
                    errors.append(f"Security scheme '{scheme_name}' must be an object")
                elif "scheme" not in scheme_def:
                    errors.append(f"Security scheme '{scheme_name}' missing required 'scheme' field")
    
    # Validate properties (optional but common)
    if "properties" in wot_td:
        if not isinstance(wot_td["properties"], dict):
            errors.append("properties must be an object")
        else:
            for prop_name, prop_def in wot_td["properties"].items():
                if not isinstance(prop_def, dict):
                    errors.append(f"Property '{prop_name}' must be an object")
                # Properties should have a type or other schema information
                if "type" not in prop_def and "oneOf" not in prop_def and "anyOf" not in prop_def:
                    warnings.append(f"Property '{prop_name}' should have type information")
    
    # Validate actions (optional)
    if "actions" in wot_td:
        if not isinstance(wot_td["actions"], dict):
            errors.append("actions must be an object")
        else:
            for action_name, action_def in wot_td["actions"].items():
                if not isinstance(action_def, dict):
                    errors.append(f"Action '{action_name}' must be an object")
    
    # Validate events (optional)
    if "events" in wot_td:
        if not isinstance(wot_td["events"], dict):
            errors.append("events must be an object")
        else:
            for event_name, event_def in wot_td["events"].items():
                if not isinstance(event_def, dict):
                    errors.append(f"Event '{event_name}' must be an object")
    
    # Check for placeholder indicator
    if "_placeholder" in wot_td:
        warnings.append("Thing Description contains placeholder marker - transformation may not be complete")
    
    # Combine errors and warnings
    all_messages = []
    if errors:
        all_messages.extend([f"ERROR: {e}" for e in errors])
    if warnings:
        all_messages.extend([f"WARNING: {w}" for w in warnings])
    
    is_valid = len(errors) == 0
    
    return is_valid, all_messages
