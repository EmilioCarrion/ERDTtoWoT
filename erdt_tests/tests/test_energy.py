"""
Tests for energy digital twin model.
"""

import pytest
from ..transformation.erdt_to_wot import transform_erdt_to_wot


class TestEnergyModel:
    """Tests for energy model."""
    
    def test_model_creation(self, energy_model):
        assert energy_model is not None
        assert "energy" in energy_model.name.lower()
    
    def test_entities(self, energy_model):
        entity_names = [e.name for e in energy_model.entities]
        assert "PowerPlant" in entity_names
        assert "Turbine" in entity_names
        assert "Grid" in entity_names
        assert "Consumer" in entity_names
    
    def test_demand_prediction(self, energy_model):
        """Test demand prediction capability."""
        consumer = energy_model.get_entity("Consumer")
        predicted_demand = consumer.get_attribute("predicted_demand")
        assert predicted_demand is not None
    
    def test_load_balancing(self, energy_model):
        """Test load balancing capability."""
        has_load_balancing = any("load" in e.name.lower() or "balance" in e.name.lower()
                                for e in energy_model.outgoing_events)
        assert has_load_balancing
    
    def test_wot_transformation(self, energy_model):
        wot_tds = transform_erdt_to_wot(energy_model)
        assert isinstance(wot_tds, dict)
        
        for entity_name, wot_td in wot_tds.items():
            assert "@context" in wot_td
            assert "title" in wot_td
