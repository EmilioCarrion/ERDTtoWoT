"""
Tests for manufacturing digital twin model.
"""

import pytest
from ..models.core import AttributeType
from ..transformation.erdt_to_wot import transform_erdt_to_wot
from ..validation.wot_validator import validate_wot_thing_description


class TestManufacturingModel:
    """Tests for manufacturing model."""
    
    def test_model_creation(self, manufacturing_model):
        assert manufacturing_model is not None
        assert "manufacturing" in manufacturing_model.name.lower()
    
    def test_entities(self, manufacturing_model):
        assert len(manufacturing_model.entities) >= 4
        entity_names = [e.name for e in manufacturing_model.entities]
        assert "ProductionLine" in entity_names
        assert "Machine" in entity_names
        assert "Sensor" in entity_names
        assert "Product" in entity_names
    
    def test_historical_attributes(self, manufacturing_model):
        """Test that machines have historical sensor data."""
        machine = manufacturing_model.get_entity("Machine")
        assert machine is not None
        
        # Should have historical temperature and vibration
        temp = machine.get_attribute("temperature")
        vibration = machine.get_attribute("vibration")
        assert temp.attribute_type == AttributeType.HISTORICAL
        assert vibration.attribute_type == AttributeType.HISTORICAL
    
    def test_predictive_maintenance(self, manufacturing_model):
        """Test that model includes predictive maintenance capability."""
        machine = manufacturing_model.get_entity("Machine")
        failure_prob = machine.get_attribute("failure_probability")
        assert failure_prob is not None
        assert failure_prob.attribute_type == AttributeType.DERIVED
    
    def test_wot_transformation(self, manufacturing_model):
        wot_td = transform_erdt_to_wot(manufacturing_model)
        is_valid, messages = validate_wot_thing_description(wot_td)
        assert "@context" in wot_td
        assert "title" in wot_td
