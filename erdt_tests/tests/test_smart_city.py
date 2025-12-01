"""
Tests for smart city digital twin model.
"""

import pytest
from ..transformation.erdt_to_wot import transform_erdt_to_wot


class TestSmartCityModel:
    """Tests for smart city model."""
    
    def test_model_creation(self, smart_city_model):
        assert smart_city_model is not None
        assert "city" in smart_city_model.name.lower()
    
    def test_entities(self, smart_city_model):
        entity_names = [e.name for e in smart_city_model.entities]
        assert "TrafficLight" in entity_names
        assert "ParkingSpot" in entity_names
        assert "StreetLight" in entity_names
        assert "AirQualitySensor" in entity_names
    
    def test_traffic_optimization(self, smart_city_model):
        """Test traffic light optimization capability."""
        traffic_light = smart_city_model.get_entity("TrafficLight")
        assert traffic_light is not None
        
        # Should have optimal timing as derived attribute
        optimal_timing = traffic_light.get_attribute("optimal_timing")
        assert optimal_timing is not None
    
    def test_energy_management(self, smart_city_model):
        """Test street light energy management."""
        # Should have outgoing event for dimming lights
        has_energy_event = any("dim" in e.name.lower() or "energy" in e.description.lower()
                              for e in smart_city_model.outgoing_events)
        assert has_energy_event
    
    def test_wot_transformation(self, smart_city_model):
        wot_tds = transform_erdt_to_wot(smart_city_model)
        assert isinstance(wot_tds, dict)
        
        for entity_name, wot_td in wot_tds.items():
            assert "@context" in wot_td
            assert "title" in wot_td
