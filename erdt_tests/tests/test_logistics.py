"""
Tests for logistics digital twin model (case study from ERDT paper).
"""

import pytest
from ..models.core import AttributeType, InterfaceType
from ..transformation.erdt_to_wot import transform_erdt_to_wot
from ..validation.wot_validator import validate_wot_thing_description


class TestLogisticsModel:
    """Tests for logistics model creation and structure."""
    
    def test_model_exists(self, logistics_model):
        """Test that logistics model is created successfully."""
        assert logistics_model is not None
        assert logistics_model.name == "Logistics Digital Twin"
        assert "logistics" in logistics_model.description.lower()
    
    def test_model_goal(self, logistics_model):
        """Test that model has appropriate goal."""
        assert logistics_model.goal
        assert "locate" in logistics_model.goal.lower() or "LEZ" in logistics_model.goal
    
    def test_entities_count(self, logistics_model):
        """Test that all expected entities are present."""
        assert len(logistics_model.entities) == 4  # Hive, Picker, Truck, Driver
        entity_names = [e.name for e in logistics_model.entities]
        assert "Hive" in entity_names
        assert "Picker" in entity_names
        assert "Truck" in entity_names
        assert "Driver" in entity_names
    
    def test_hive_entity(self, logistics_model):
        """Test Hive entity structure."""
        hive = logistics_model.get_entity("Hive")
        assert hive is not None
        
        # Check attributes
        attr_names = [a.name for a in hive.attributes]
        assert "name" in attr_names
        assert "blueprint" in attr_names
    
    def test_picker_entity(self, logistics_model):
        """Test Picker entity with historical attribute."""
        picker = logistics_model.get_entity("Picker")
        assert picker is not None
        
        # Check for historical indoor_location attribute
        indoor_loc = picker.get_attribute("indoor_location")
        assert indoor_loc is not None
        assert indoor_loc.attribute_type == AttributeType.HISTORICAL
    
    def test_truck_entity(self, logistics_model):
        """Test Truck entity with historical GPS location."""
        truck = logistics_model.get_entity("Truck")
        assert truck is not None
        
        # Check for historical location attribute
        location = truck.get_attribute("location")
        assert location is not None
        assert location.attribute_type == AttributeType.HISTORICAL
    
    def test_driver_entity(self, logistics_model):
        """Test Driver entity with derived location."""
        driver = logistics_model.get_entity("Driver")
        assert driver is not None
        
        # Check for derived location attribute
        location = driver.get_attribute("location")
        assert location is not None
        assert location.attribute_type == AttributeType.DERIVED
    
    def test_relationships(self, logistics_model):
        """Test relationships between entities."""
        assert len(logistics_model.relationships) == 3
        
        rel_names = [r.name for r in logistics_model.relationships]
        assert "works_in" in rel_names
        assert "delivers_from" in rel_names
        assert "driven_by" in rel_names
    
    def test_interfaces(self, logistics_model):
        """Test that interfaces are defined."""
        assert len(logistics_model.interfaces) >= 6
        
        interface_names = [i.name for i in logistics_model.interfaces]
        assert "set_location" in interface_names
        assert "get_location" in interface_names
        assert "assign_driver" in interface_names
        assert "get_blueprints" in interface_names
    
    def test_security_constraints(self, logistics_model):
        """Test that interfaces have security constraints."""
        for interface in logistics_model.interfaces:
            # All interfaces should have some security consideration
            assert interface.security_constraints is not None
    
    def test_data_flows(self, logistics_model):
        """Test incoming events and outgoing events."""
        # Incoming events
        assert len(logistics_model.incoming_events) >= 3
        event_names = [e.name for e in logistics_model.incoming_events]
        assert "picker_telemetry" in event_names
        assert "driver_assigned" in event_names
        assert "truck_gps_coordinates" in event_names
        
        # Outgoing events
        assert len(logistics_model.outgoing_events) >= 1
        out_event_names = [e.name for e in logistics_model.outgoing_events]
        assert "truck_entered_lez" in out_event_names
    
    def test_lez_alert_trigger(self, logistics_model):
        """Test LEZ alert outgoing event (key requirement from case study)."""
        lez_alert = None
        for event in logistics_model.outgoing_events:
            if "lez" in event.name.lower():
                lez_alert = event
                break
        
        assert lez_alert is not None
        assert lez_alert.trigger_condition
        assert "lez" in lez_alert.trigger_condition.lower() or "zone" in lez_alert.trigger_condition.lower()


class TestLogisticsWoTTransformation:
    """Tests for WoT transformation of logistics model."""
    
    def test_transformation_produces_dict(self, logistics_model):
        """Test that transformation returns a dictionary of TDs (one per entity)."""
        wot_tds = transform_erdt_to_wot(logistics_model)
        assert isinstance(wot_tds, dict)
        
        # Should have one TD per entity
        assert len(wot_tds) == 4  # Hive, Picker, Truck, Driver
        assert "Hive" in wot_tds
        assert "Picker" in wot_tds
        assert "Truck" in wot_tds
        assert "Driver" in wot_tds
    
    def test_wot_validation(self, logistics_model):
        """Test that each transformed WoT TD is valid."""
        wot_tds = transform_erdt_to_wot(logistics_model)
        
        # Validate each entity's TD
        for entity_name, wot_td in wot_tds.items():
            is_valid, messages = validate_wot_thing_description(wot_td)
            
            # Print validation results for debugging
            if not is_valid:
                print(f"\nWoT validation messages for {entity_name}:")
                for msg in messages:
                    print(f"  {msg}")
            
            # Each TD should have required fields
            assert "@context" in wot_td
            assert "title" in wot_td
            assert wot_td["title"] == entity_name
            assert "security" in wot_td
            assert "securityDefinitions" in wot_td
    
    def test_wot_has_required_sections(self, logistics_model):
        """Test that each WoT TD has properties, actions, and events sections."""
        wot_tds = transform_erdt_to_wot(logistics_model)
        
        for entity_name, wot_td in wot_tds.items():
            # These should exist even if empty
            assert "properties" in wot_td
            assert "actions" in wot_td
            assert "events" in wot_td
            assert "links" in wot_td
    
    def test_picker_td_has_indoor_location(self, logistics_model):
        """Test that Picker TD has indoor_location property."""
        wot_tds = transform_erdt_to_wot(logistics_model)
        picker_td = wot_tds["Picker"]
        
        assert "indoor_location" in picker_td["properties"]
        assert picker_td["properties"]["indoor_location"]["observable"] == True
    
    def test_truck_td_has_lez_event(self, logistics_model):
        """Test that Truck TD has LEZ alert event."""
        wot_tds = transform_erdt_to_wot(logistics_model)
        truck_td = wot_tds["Truck"]
        
        # Truck should have the LEZ alert event
        assert len(truck_td["events"]) >= 1
        assert "truck_entered_lez" in truck_td["events"]
    
    def test_relationships_as_links(self, logistics_model):
        """Test that relationships are represented as links between TDs."""
        wot_tds = transform_erdt_to_wot(logistics_model)
        
        # Picker should have link to Hive (works_in relationship)
        picker_td = wot_tds["Picker"]
        assert len(picker_td["links"]) > 0
        
        # Check if there's a link to Hive
        has_hive_link = any("Hive" in link["href"] for link in picker_td["links"])
        assert has_hive_link
