"""
Tests for healthcare digital twin model.
"""

import pytest
from ..transformation.erdt_to_wot import transform_erdt_to_wot
from ..validation.wot_validator import validate_wot_thing_description


class TestHealthcareModel:
    """Tests for healthcare model."""
    
    def test_model_creation(self, healthcare_model):
        assert healthcare_model is not None
        assert "healthcare" in healthcare_model.name.lower()
    
    def test_entities(self, healthcare_model):
        assert len(healthcare_model.entities) >= 4
        entity_names = [e.name for e in healthcare_model.entities]
        assert "Patient" in entity_names
        assert "MedicalDevice" in entity_names
        assert "VitalSigns" in entity_names
        assert "Treatment" in entity_names
    
    def test_vital_signs_historical(self, healthcare_model):
        """Test that vital signs are tracked historically."""
        from ..models.core import AttributeType
        vitals = healthcare_model.get_entity("VitalSigns")
        assert vitals is not None
        
        # All vital signs should be historical
        heart_rate = vitals.get_attribute("heart_rate")
        assert heart_rate.attribute_type == AttributeType.HISTORICAL
    
    def test_emergency_alerts(self, healthcare_model):
        """Test that model includes emergency alert capability."""
        assert len(healthcare_model.outgoing_events) >= 1
        
        # Should have emergency alert
        has_emergency = any("emergency" in e.name.lower() or "alert" in e.name.lower() 
                           for e in healthcare_model.outgoing_events)
        assert has_emergency
    
    def test_security_hipaa(self, healthcare_model):
        """Test that interfaces mention HIPAA compliance."""
        has_hipaa = any("HIPAA" in str(i.security_constraints) 
                       for i in healthcare_model.interfaces)
        assert has_hipaa
    
    def test_wot_transformation(self, healthcare_model):
        wot_tds = transform_erdt_to_wot(healthcare_model)
        assert isinstance(wot_tds, dict)
        
        # Each TD should have required fields
        for entity_name, wot_td in wot_tds.items():
            assert "@context" in wot_td
            assert "title" in wot_td
