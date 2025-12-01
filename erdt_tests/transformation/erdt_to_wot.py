"""
ERDT to WoT Thing Description transformation.

This module transforms ERDT models to WoT Thing Descriptions following the W3C WoT specification.
"""

from typing import Dict, Any, List
from ..models.core import (
    ERDTModel,
    Entity,
    Attribute,
    HistoricalAttribute,
    DerivedAttribute,
    AttributeType,
    Interface,
    InterfaceType,
    IncomingEvent,
    OutgoingEvent,
)


def _map_value_set_to_json_schema(value_set_name: str) -> Dict[str, Any]:
    """
    Map ERDT ValueSet to JSON Schema type.
    
    Args:
        value_set_name: Name of the value set
        
    Returns:
        JSON Schema type definition
    """
    # Common type mappings
    type_mapping = {
        "String": {"type": "string"},
        "Integer": {"type": "integer"},
        "Float": {"type": "number"},
        "Boolean": {"type": "boolean"},
        "DateTime": {"type": "string", "format": "date-time"},
        "GeoCoordinates": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            }
        },
    }
    
    # Return mapped type or default to object for custom types
    return type_mapping.get(value_set_name, {"type": "object", "description": value_set_name})


def _create_property_from_attribute(
    entity_name: str,
    attribute: Attribute,
    writable_attributes: set
) -> Dict[str, Any]:
    """
    Create a WoT property from an ERDT attribute.
    
    Args:
        entity_name: Name of the entity this attribute belongs to
        attribute: The ERDT attribute
        writable_attributes: Set of attribute names that are writable via interfaces
        
    Returns:
        WoT property definition
    """
    property_def = _map_value_set_to_json_schema(attribute.value_set.name)
    
    # Add description
    if attribute.description:
        property_def["description"] = attribute.description
    
    # Historical attributes are observable
    if attribute.attribute_type == AttributeType.HISTORICAL:
        property_def["observable"] = True
        property_def["description"] = property_def.get("description", "") + " (time-series data)"
    
    # Derived attributes are read-only
    if attribute.attribute_type == AttributeType.DERIVED:
        property_def["readOnly"] = True
        if hasattr(attribute, 'computation_description') and attribute.computation_description:
            property_def["description"] = property_def.get("description", "") + f" [Computed: {attribute.computation_description}]"
    
    # Check if writable based on interfaces
    attr_key = f"{entity_name}_{attribute.name}"
    if attr_key in writable_attributes:
        property_def["readOnly"] = False
    else:
        property_def["readOnly"] = property_def.get("readOnly", True)
    
    return property_def


def _create_action_from_interface(interface: Interface) -> Dict[str, Any]:
    """
    Create a WoT action from an ERDT interface.
    
    Args:
        interface: The ERDT interface
        
    Returns:
        WoT action definition
    """
    action_def = {}
    
    if interface.description:
        action_def["description"] = interface.description
    
    # Add input schema if parameters exist
    if interface.parameters:
        action_def["input"] = {
            "type": "object",
            "properties": {
                param: {"type": "string"}  # Default to string, could be enhanced
                for param in interface.parameters
            },
            "required": interface.parameters
        }
    
    # Add output schema if returns exist
    if interface.returns:
        action_def["output"] = {
            "type": "object",
            "description": interface.returns
        }
    
    # Add security information
    if interface.security_constraints:
        action_def["security"] = interface.security_constraints
    
    return action_def


def _create_event_from_outgoing_event(outgoing_event: OutgoingEvent) -> Dict[str, Any]:
    """
    Create a WoT event from an ERDT outgoing event.
    
    Args:
        outgoing_event: The ERDT outgoing event
        
    Returns:
        WoT event definition
    """
    event_def = {}
    
    if outgoing_event.description:
        event_def["description"] = outgoing_event.description
    
    # Add trigger condition as part of description
    if outgoing_event.trigger_condition:
        event_def["description"] = event_def.get("description", "") + f" (Triggered when: {outgoing_event.trigger_condition})"
    
    # Add event target information
    if outgoing_event.event_target:
        event_def["target"] = outgoing_event.event_target
    
    # Default event data schema
    event_def["data"] = {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "source": {"type": "string"},
            "data": {"type": "object"}
        }
    }
    
    return event_def


def transform_erdt_to_wot(erdt_model: ERDTModel) -> Dict[str, Any]:
    """
    Transform an ERDT model to a WoT Thing Description.
    
    This transformation maps:
    - ERDT Entities + Attributes -> WoT Properties
    - ERDT Historical Attributes -> WoT Properties (observable)
    - ERDT Derived Attributes -> WoT Properties (readOnly)
    - ERDT Interfaces (Query) -> WoT Properties (readable)
    - ERDT Interfaces (Update/Analytical) -> WoT Actions
    - ERDT Incoming Events -> WoT Actions (invokable to trigger updates)
    - ERDT Outgoing Events -> WoT Events
    
    Args:
        erdt_model: The ERDT model to transform
        
    Returns:
        A dictionary representing a WoT Thing Description
    """
    
    # Initialize WoT Thing Description
    wot_td = {
        "@context": [
            "https://www.w3.org/2019/wot/td/v1",
            {
                "erdt": "https://erdt.example.org/",
                "iot": "http://iotschema.org/"
            }
        ],
        "title": erdt_model.name,
        "description": erdt_model.description or f"Digital Twin: {erdt_model.name}",
        "@type": "Thing",
        "security": ["basic_sc"],
        "securityDefinitions": {
            "basic_sc": {
                "scheme": "basic",
                "in": "header"
            },
            "nosec_sc": {
                "scheme": "nosec"
            }
        },
        "properties": {},
        "actions": {},
        "events": {}
    }
    
    # Add goal as metadata
    if erdt_model.goal:
        wot_td["erdt:goal"] = erdt_model.goal
    
    # Track which attributes are writable based on interfaces
    writable_attributes = set()
    for interface in erdt_model.interfaces:
        if interface.interface_type == InterfaceType.UPDATE:
            # Mark attributes that can be updated via this interface
            for param in interface.parameters:
                writable_attributes.add(f"{interface.entity.name}_{param}")
    
    # Transform entities and their attributes to properties
    for entity in erdt_model.entities:
        for attribute in entity.attributes:
            property_name = f"{entity.name}_{attribute.name}"
            wot_td["properties"][property_name] = _create_property_from_attribute(
                entity.name,
                attribute,
                writable_attributes
            )
    
    # Transform interfaces to actions
    for interface in erdt_model.interfaces:
        # Query interfaces can be represented as readable properties (already done above)
        # Update, Relationship, and Analytical interfaces become actions
        if interface.interface_type in [InterfaceType.UPDATE, InterfaceType.RELATIONSHIP, InterfaceType.ANALYTICAL]:
            action_name = f"{interface.entity.name}_{interface.name}"
            wot_td["actions"][action_name] = _create_action_from_interface(interface)
    
    # Transform incoming events to actions (they can be invoked to update the DT)
    for incoming_event in erdt_model.incoming_events:
        action_name = f"trigger_{incoming_event.name}"
        action_def = {
            "description": incoming_event.description or f"Trigger incoming event: {incoming_event.name}",
            "input": {
                "type": "object",
                "properties": {
                    "value": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        }
        
        if incoming_event.event_source:
            action_def["erdt:eventSource"] = incoming_event.event_source
        
        wot_td["actions"][action_name] = action_def
    
    # Transform outgoing events to WoT events
    for outgoing_event in erdt_model.outgoing_events:
        event_name = outgoing_event.name
        wot_td["events"][event_name] = _create_event_from_outgoing_event(outgoing_event)
    
    # Add relationships as metadata
    if erdt_model.relationships:
        wot_td["erdt:relationships"] = [
            {
                "name": rel.name,
                "entities": [e.name for e in rel.entities],
                "description": rel.description
            }
            for rel in erdt_model.relationships
        ]
    
    return wot_td
