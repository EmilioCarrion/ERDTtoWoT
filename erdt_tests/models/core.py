"""
Core classes for Entity-Relationship Digital Twin (ERDT) modeling.

This module implements the conceptual modeling constructs defined in the ERDT method,
including entities, attributes (regular, historical, derived), relationships, interfaces,
and data flows (incoming events and outgoing events).
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, List, Dict
from enum import Enum


class ValueSet:
    """
    Represents a domain of values for attributes.
    
    Examples: String, Integer, Float, Boolean, DateTime, GeoCoordinates, etc.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def __repr__(self) -> str:
        return f"ValueSet({self.name})"


class AttributeType(Enum):
    """Types of attributes in ERDT models."""
    REGULAR = "regular"
    HISTORICAL = "historical"
    DERIVED = "derived"


@dataclass
class Attribute:
    """
    Base attribute class representing a property of an entity or relationship.
    
    Attributes map entities to value sets.
    """
    name: str
    value_set: ValueSet
    description: str = ""
    attribute_type: AttributeType = AttributeType.REGULAR
    
    def __repr__(self) -> str:
        return f"Attribute({self.name}: {self.value_set.name})"


@dataclass
class HistoricalAttribute(Attribute):
    """
    Historical attribute that stores time-series data.
    
    As defined in the ERDT method, historical attributes map to ordered sets
    of pairs (value, timestamp), allowing tracking of data evolution over time.
    This is essential for machine learning, analysis, and predictions.
    """
    
    def __init__(self, name: str, value_set: ValueSet, description: str = ""):
        super().__init__(
            name=name,
            value_set=value_set,
            description=description,
            attribute_type=AttributeType.HISTORICAL
        )
    
    def __repr__(self) -> str:
        return f"HistoricalAttribute({self.name}: {self.value_set.name})"


@dataclass
class DerivedAttribute(Attribute):
    """
    Derived attribute computed from other attributes.
    
    Can represent analytical models, physics equations, machine learning predictions,
    or any computed value based on sensor data or other attributes.
    """
    computation_description: str = ""
    
    def __init__(
        self,
        name: str,
        value_set: ValueSet,
        description: str = "",
        computation_description: str = ""
    ):
        super().__init__(
            name=name,
            value_set=value_set,
            description=description,
            attribute_type=AttributeType.DERIVED
        )
        self.computation_description = computation_description
    
    def __repr__(self) -> str:
        return f"DerivedAttribute({self.name}: {self.value_set.name})"


@dataclass
class Entity:
    """
    Represents an entity set in the ERDT model.
    
    Entities correspond to physical or logical components in the digital twin,
    such as machines, sensors, vehicles, people, etc.
    """
    name: str
    attributes: List[Attribute] = field(default_factory=list)
    description: str = ""
    
    def add_attribute(self, attribute: Attribute) -> None:
        """Add an attribute to this entity."""
        self.attributes.append(attribute)
    
    def get_attribute(self, name: str) -> Optional[Attribute]:
        """Get an attribute by name."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        return None
    
    def __repr__(self) -> str:
        return f"Entity({self.name}, {len(self.attributes)} attributes)"


@dataclass
class Relationship:
    """
    Represents a relationship between entities.
    
    Relationships can have their own attributes and cardinality constraints.
    """
    name: str
    entities: List[Entity]
    attributes: List[Attribute] = field(default_factory=list)
    cardinality: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    
    def __repr__(self) -> str:
        entity_names = [e.name for e in self.entities]
        return f"Relationship({self.name}: {' - '.join(entity_names)})"


class InterfaceType(Enum):
    """Types of interfaces in ERDT models."""
    QUERY = "query"  # Read-only access
    UPDATE = "update"  # Modify attributes
    RELATIONSHIP = "relationship"  # Create/modify relationships
    ANALYTICAL = "analytical"  # Complex computations


@dataclass
class Interface:
    """
    Represents an interface for accessing or modifying entity data.
    
    Interfaces handle security constraints and encapsulation, ensuring that
    only authorized parties can access or update the digital twin.
    
    As defined in ERDT: I: F × E_i × P(V) → F
    """
    name: str
    entity: Entity
    interface_type: InterfaceType
    description: str = ""
    security_constraints: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Interface({self.name} on {self.entity.name})"


class DataFlowType(Enum):
    """Types of data flows in ERDT models."""
    INCOMING_EVENT = "incoming_event"
    OUTGOING_EVENT = "outgoing_event"


@dataclass
class IncomingEvent:
    """
    Represents an event or data flow from a physical component to the digital twin.
    
    Incoming events update the digital twin when the physical entity's state changes.
    They use interfaces to populate entity attributes or relationships.
    
    As defined in ERDT: IE: F × E_i × V → F
    """
    name: str
    target_interface: Interface
    description: str = ""
    event_source: str = ""  # Description of physical source
    
    def __repr__(self) -> str:
        return f"IncomingEvent({self.name} -> {self.target_interface.name})"


@dataclass
class OutgoingEvent:
    """
    Represents a command or event issued by the digital twin to the physical world.
    
    Outgoing events enable closed-loop control, allowing the DT to actuate
    changes in the physical environment based on analysis or predictions.
    """
    name: str
    source_interface: Interface
    description: str = ""
    event_target: str = ""  # Description of physical target (actuator, system, etc.)
    trigger_condition: str = ""  # What causes this event to be issued
    
    def __repr__(self) -> str:
        return f"OutgoingEvent({self.name} from {self.source_interface.name})"


@dataclass
class ERDTModel:
    """
    Main container for a complete ERDT model.
    
    Represents the entire digital twin conceptual model including entities,
    relationships, interfaces, and data flows.
    """
    name: str
    description: str = ""
    goal: str = ""  # The objective of this digital twin
    entities: List[Entity] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    interfaces: List[Interface] = field(default_factory=list)
    incoming_events: List[IncomingEvent] = field(default_factory=list)
    outgoing_events: List[OutgoingEvent] = field(default_factory=list)
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the model."""
        self.entities.append(entity)
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the model."""
        self.relationships.append(relationship)
    
    def add_interface(self, interface: Interface) -> None:
        """Add an interface to the model."""
        self.interfaces.append(interface)
    
    def add_incoming_event(self, event: IncomingEvent) -> None:
        """Add an incoming event to the model."""
        self.incoming_events.append(event)
    
    def add_outgoing_event(self, event: OutgoingEvent) -> None:
        """Add an outgoing event to the model."""
        self.outgoing_events.append(event)
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """Get an entity by name."""
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None
    
    def summary(self) -> str:
        """Get a summary of the model."""
        return f"""
ERDT Model: {self.name}
Goal: {self.goal}
Description: {self.description}

Entities: {len(self.entities)}
Relationships: {len(self.relationships)}
Interfaces: {len(self.interfaces)}
Incoming Events: {len(self.incoming_events)}
Outgoing Events: {len(self.outgoing_events)}
        """.strip()
    
    def __repr__(self) -> str:
        return f"ERDTModel({self.name}, {len(self.entities)} entities)"
