"""
Tests for core ERDT model classes.
"""

import pytest
from ..models.core import (
    ValueSet,
    Attribute,
    HistoricalAttribute,
    DerivedAttribute,
    AttributeType,
    Entity,
    Relationship,
    Interface,
    InterfaceType,
    IncomingEvent,
    OutgoingEvent,
    ERDTModel,
)


class TestValueSet:
    """Tests for ValueSet class."""
    
    def test_value_set_creation(self):
        vs = ValueSet("String", "Text values")
        assert vs.name == "String"
        assert vs.description == "Text values"
    
    def test_value_set_repr(self):
        vs = ValueSet("Integer")
        assert "Integer" in repr(vs)


class TestAttributes:
    """Tests for Attribute classes."""
    
    def test_regular_attribute(self):
        vs = ValueSet("Float")
        attr = Attribute("temperature", vs, "Temperature in Celsius")
        assert attr.name == "temperature"
        assert attr.value_set == vs
        assert attr.description == "Temperature in Celsius"
        assert attr.attribute_type == AttributeType.REGULAR
    
    def test_historical_attribute(self):
        vs = ValueSet("Float")
        attr = HistoricalAttribute("temperature", vs, "Temperature over time")
        assert attr.name == "temperature"
        assert attr.attribute_type == AttributeType.HISTORICAL
        assert "HistoricalAttribute" in repr(attr)
    
    def test_derived_attribute(self):
        vs = ValueSet("Float")
        attr = DerivedAttribute(
            "efficiency",
            vs,
            "Production efficiency",
            "Calculated from output/input"
        )
        assert attr.name == "efficiency"
        assert attr.attribute_type == AttributeType.DERIVED
        assert attr.computation_description == "Calculated from output/input"
        assert "DerivedAttribute" in repr(attr)


class TestEntity:
    """Tests for Entity class."""
    
    def test_entity_creation(self):
        entity = Entity("Machine", description="Manufacturing machine")
        assert entity.name == "Machine"
        assert entity.description == "Manufacturing machine"
        assert len(entity.attributes) == 0
    
    def test_add_attribute(self):
        entity = Entity("Machine")
        vs = ValueSet("String")
        attr = Attribute("id", vs)
        entity.add_attribute(attr)
        assert len(entity.attributes) == 1
        assert entity.attributes[0] == attr
    
    def test_get_attribute(self):
        entity = Entity("Machine")
        vs = ValueSet("String")
        attr = Attribute("id", vs)
        entity.add_attribute(attr)
        
        found = entity.get_attribute("id")
        assert found == attr
        
        not_found = entity.get_attribute("nonexistent")
        assert not_found is None


class TestRelationship:
    """Tests for Relationship class."""
    
    def test_relationship_creation(self):
        entity1 = Entity("Machine")
        entity2 = Entity("Sensor")
        rel = Relationship("monitors", [entity1, entity2], description="Sensor monitors machine")
        
        assert rel.name == "monitors"
        assert len(rel.entities) == 2
        assert entity1 in rel.entities
        assert entity2 in rel.entities
        assert rel.description == "Sensor monitors machine"


class TestInterface:
    """Tests for Interface class."""
    
    def test_interface_creation(self):
        entity = Entity("Machine")
        interface = Interface(
            "get_status",
            entity,
            InterfaceType.QUERY,
            "Get machine status",
            security_constraints=["Requires authentication"],
            parameters=["timestamp"],
            returns="Status object"
        )
        
        assert interface.name == "get_status"
        assert interface.entity == entity
        assert interface.interface_type == InterfaceType.QUERY
        assert interface.description == "Get machine status"
        assert "Requires authentication" in interface.security_constraints
        assert "timestamp" in interface.parameters
        assert interface.returns == "Status object"


class TestDataFlows:
    """Tests for data flow classes."""
    
    def test_incoming_event(self):
        entity = Entity("Sensor")
        interface = Interface("update_value", entity, InterfaceType.UPDATE)
        event = IncomingEvent(
            "sensor_reading",
            interface,
            "Sensor emits reading",
            "IoT sensor device"
        )
        
        assert event.name == "sensor_reading"
        assert event.target_interface == interface
        assert event.description == "Sensor emits reading"
        assert event.event_source == "IoT sensor device"
    
    def test_outgoing_event(self):
        entity = Entity("Machine")
        interface = Interface("set_status", entity, InterfaceType.UPDATE)
        event = OutgoingEvent(
            "alert",
            interface,
            "Critical alert",
            "Monitoring system",
            "Temperature exceeds threshold"
        )
        
        assert event.name == "alert"
        assert event.source_interface == interface
        assert event.event_target == "Monitoring system"
        assert event.trigger_condition == "Temperature exceeds threshold"


class TestERDTModel:
    """Tests for ERDTModel class."""
    
    def test_model_creation(self):
        model = ERDTModel(
            "Test DT",
            "Test digital twin",
            "Testing purposes"
        )
        
        assert model.name == "Test DT"
        assert model.description == "Test digital twin"
        assert model.goal == "Testing purposes"
        assert len(model.entities) == 0
    
    def test_add_components(self):
        model = ERDTModel("Test DT")
        
        # Add entity
        entity = Entity("Machine")
        model.add_entity(entity)
        assert len(model.entities) == 1
        
        # Add relationship
        entity2 = Entity("Sensor")
        model.add_entity(entity2)
        rel = Relationship("monitors", [entity, entity2])
        model.add_relationship(rel)
        assert len(model.relationships) == 1
        
        # Add interface
        interface = Interface("get_status", entity, InterfaceType.QUERY)
        model.add_interface(interface)
        assert len(model.interfaces) == 1
        
        # Add data flows
        event = IncomingEvent("reading", interface)
        model.add_incoming_event(event)
        assert len(model.incoming_events) == 1
        
        out_event = OutgoingEvent("alert", interface)
        model.add_outgoing_event(out_event)
        assert len(model.outgoing_events) == 1
    
    def test_get_entity(self):
        model = ERDTModel("Test DT")
        entity = Entity("Machine")
        model.add_entity(entity)
        
        found = model.get_entity("Machine")
        assert found == entity
        
        not_found = model.get_entity("Nonexistent")
        assert not_found is None
    
    def test_summary(self):
        model = ERDTModel("Test DT", "Description", "Goal")
        model.add_entity(Entity("Machine"))
        
        summary = model.summary()
        assert "Test DT" in summary
        assert "Goal" in summary
        assert "1" in summary  # 1 entity
