"""
Tests for agriculture digital twin model.
"""

import pytest
from ..transformation.erdt_to_wot import transform_erdt_to_wot


class TestAgricultureModel:
    """Tests for agriculture model."""
    
    def test_model_creation(self, agriculture_model):
        assert agriculture_model is not None
        assert "agriculture" in agriculture_model.name.lower()
    
    def test_entities(self, agriculture_model):
        entity_names = [e.name for e in agriculture_model.entities]
        assert "Field" in entity_names
        assert "Crop" in entity_names
        assert "IrrigationSystem" in entity_names
        assert "WeatherStation" in entity_names
    
    def test_yield_prediction(self, agriculture_model):
        """Test crop yield prediction capability."""
        crop = agriculture_model.get_entity("Crop")
        predicted_yield = crop.get_attribute("predicted_yield")
        assert predicted_yield is not None
    
    def test_irrigation_control(self, agriculture_model):
        """Test automated irrigation control."""
        has_irrigation = any("irrigation" in e.name.lower()
                            for e in agriculture_model.outgoing_events)
        assert has_irrigation
    
    def test_soil_monitoring(self, agriculture_model):
        """Test soil condition monitoring."""
        field = agriculture_model.get_entity("Field")
        soil_moisture = field.get_attribute("soil_moisture")
        assert soil_moisture is not None
    
    def test_wot_transformation(self, agriculture_model):
        wot_tds = transform_erdt_to_wot(agriculture_model)
        assert isinstance(wot_tds, dict)
        
        for entity_name, wot_td in wot_tds.items():
            assert "@context" in wot_td
            assert "title" in wot_td
