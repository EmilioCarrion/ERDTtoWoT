"""
ERDT to WoT Thing Description transformation.

This module transforms ERDT models to WoT Thing Descriptions following the W3C WoT specification.
Each ERDT Entity becomes a separate WoT Thing.
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
    
    # Add required forms field with HTTP binding
    property_def["forms"] = [{
        "href": f"https://example.com/things/{entity_name}/properties/{attribute.name}",
        "contentType": "application/json",
        "op": ["readproperty", "writeproperty"] if not property_def.get("readOnly", True) else ["readproperty"]
    }]
    
    return property_def


def _create_action_from_interface(entity_name: str, interface: Interface) -> Dict[str, Any]:
    """
    Create a WoT action from an ERDT interface.
    
    Args:
        entity_name: Name of the entity
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
    
    # Add required forms field
    action_def["forms"] = [{
        "href": f"https://example.com/things/{entity_name}/actions/{interface.name}",
        "contentType": "application/json",
        "op": "invokeaction"
    }]
    
    return action_def


def _create_event_from_outgoing_event(entity_name: str, outgoing_event: OutgoingEvent) -> Dict[str, Any]:
    """
    Create a WoT event from an ERDT outgoing event.
    
    Args:
        entity_name: Name of the entity
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
    
    # Add required forms field with SSE (Server-Sent Events) binding
    event_def["forms"] = [{
        "href": f"https://example.com/things/{entity_name}/events/{outgoing_event.name}",
        "contentType": "application/json",
        "subprotocol": "sse",
        "op": "subscribeevent"
    }]
    
    return event_def


def transform_erdt_to_wot(erdt_model: ERDTModel) -> Dict[str, Dict[str, Any]]:
    """
    Transform an ERDT model to WoT Thing Descriptions.
    
    **IMPORTANT**: This creates ONE Thing Description per ERDT Entity.
    Each entity becomes an independent WoT Thing with its own properties, actions, and events.
    
    Mapping:
    - ERDT Entity → WoT Thing (one TD per entity)
    - ERDT Attributes → WoT Properties (of that entity's TD)
    - ERDT Interfaces → WoT Actions (of the entity's TD)
    - ERDT Incoming Events → WoT Actions (for the target entity)
    - ERDT Outgoing Events → WoT Events (for the source entity)
    - ERDT Relationships → Links between TDs
    
    Args:
        erdt_model: The ERDT model to transform
        
    Returns:
        A dictionary mapping entity names to their WoT Thing Descriptions
        Format: {"EntityName": {...WoT TD...}, ...}
    """
    
    # Dictionary to hold all Thing Descriptions (one per entity)
    thing_descriptions = {}
    
    # Track which attributes are writable based on interfaces
    writable_attributes = set()
    for interface in erdt_model.interfaces:
        if interface.interface_type == InterfaceType.UPDATE:
            for param in interface.parameters:
                writable_attributes.add(f"{interface.entity.name}_{param}")
    
    # Create a Thing Description for each entity
    for entity in erdt_model.entities:
        # Initialize WoT Thing Description for this entity
        wot_td = {
            "@context": [
                "https://www.w3.org/2019/wot/td/v1",
                {
                    "erdt": "https://erdt.example.org/",
                    "iot": "http://iotschema.org/"
                }
            ],
            "id": f"urn:uuid:{entity.name.lower()}",
            "title": entity.name,
            "description": entity.description or f"Digital Twin of {entity.name}",
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
            "events": {},
            "links": []
        }
        
        # Add ERDT model goal as metadata
        if erdt_model.goal:
            wot_td["erdt:modelGoal"] = erdt_model.goal
        
        # Transform entity's attributes to properties
        for attribute in entity.attributes:
            property_name = attribute.name
            wot_td["properties"][property_name] = _create_property_from_attribute(
                entity.name,
                attribute,
                writable_attributes
            )
        
        # Transform interfaces that belong to this entity to actions
        for interface in erdt_model.interfaces:
            if interface.entity.name == entity.name:
                if interface.interface_type in [InterfaceType.UPDATE, InterfaceType.RELATIONSHIP, InterfaceType.ANALYTICAL]:
                    action_name = interface.name
                    wot_td["actions"][action_name] = _create_action_from_interface(entity.name, interface)
        
        # Transform incoming events that target this entity's interfaces
        for incoming_event in erdt_model.incoming_events:
            if incoming_event.target_interface.entity.name == entity.name:
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
                
                # Add required forms field
                action_def["forms"] = [{
                    "href": f"https://example.com/things/{entity.name}/actions/trigger_{incoming_event.name}",
                    "contentType": "application/json",
                    "op": "invokeaction"
                }]
                
                wot_td["actions"][action_name] = action_def
        
        # Transform outgoing events that originate from this entity's interfaces
        for outgoing_event in erdt_model.outgoing_events:
            if outgoing_event.source_interface.entity.name == entity.name:
                event_name = outgoing_event.name
                wot_td["events"][event_name] = _create_event_from_outgoing_event(entity.name, outgoing_event)
        
        # Add relationships as links to other Things
        for relationship in erdt_model.relationships:
            if entity in relationship.entities:
                # Find the other entity/entities in this relationship
                other_entities = [e for e in relationship.entities if e.name != entity.name]
                for other_entity in other_entities:
                    wot_td["links"].append({
                        "rel": relationship.name,
                        "href": f"https://example.com/things/{other_entity.name}",
                        "type": "application/td+json",
                        "erdt:relationshipDescription": relationship.description
                    })
        
        # Store this entity's Thing Description
        thing_descriptions[entity.name] = wot_td
    
    return thing_descriptions
