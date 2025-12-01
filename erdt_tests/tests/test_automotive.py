"""
Tests for automotive digital twin model.
"""

import pytest
from ..transformation.erdt_to_wot import transform_erdt_to_wot
from ..validation.wot_validator import validate_wot_thing_description


class TestAutomotiveModel:
    """Tests for automotive model."""
    
    def test_model_creation(self, automotive_model):
        assert automotive_model is not None
        assert "automotive" in automotive_model.name.lower() or "vehicle" in automotive_model.name.lower()
    
    def test_entities(self, automotive_model):
        entity_names = [e.name for e in automotive_model.entities]
        assert "Vehicle" in entity_names
        assert "Engine" in entity_names
        assert "Battery" in entity_names
        assert "Driver" in entity_names
    
    def test_diagnostics(self, automotive_model):
        """Test vehicle diagnostics capability."""
        has_diagnostics = any("diagnostic" in i.name.lower() 
                             for i in automotive_model.interfaces)
        assert has_diagnostics
    
    def test_safety_alerts(self, automotive_model):
        """Test safety alert system."""
        has_safety = any("safety" in e.name.lower() or "alert" in e.name.lower()
                        for e in automotive_model.outgoing_events)
        assert has_safety
    
    def test_wot_transformation(self, automotive_model):
        wot_td = transform_erdt_to_wot(automotive_model)
        assert "@context" in wot_td
