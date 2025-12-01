"""
Pytest configuration and fixtures for ERDT tests.
"""

import pytest
from ..models.industries.logistics import create_logistics_model
from ..models.industries.manufacturing import create_manufacturing_model
from ..models.industries.healthcare import create_healthcare_model
from ..models.industries.smart_city import create_smart_city_model
from ..models.industries.automotive import create_automotive_model
from ..models.industries.energy import create_energy_model
from ..models.industries.agriculture import create_agriculture_model


@pytest.fixture
def logistics_model():
    """Fixture for logistics digital twin model."""
    return create_logistics_model()


@pytest.fixture
def manufacturing_model():
    """Fixture for manufacturing digital twin model."""
    return create_manufacturing_model()


@pytest.fixture
def healthcare_model():
    """Fixture for healthcare digital twin model."""
    return create_healthcare_model()


@pytest.fixture
def smart_city_model():
    """Fixture for smart city digital twin model."""
    return create_smart_city_model()


@pytest.fixture
def automotive_model():
    """Fixture for automotive digital twin model."""
    return create_automotive_model()


@pytest.fixture
def energy_model():
    """Fixture for energy digital twin model."""
    return create_energy_model()


@pytest.fixture
def agriculture_model():
    """Fixture for agriculture digital twin model."""
    return create_agriculture_model()


@pytest.fixture
def all_models(
    logistics_model,
    manufacturing_model,
    healthcare_model,
    smart_city_model,
    automotive_model,
    energy_model,
    agriculture_model
):
    """Fixture providing all industry models."""
    return {
        "logistics": logistics_model,
        "manufacturing": manufacturing_model,
        "healthcare": healthcare_model,
        "smart_city": smart_city_model,
        "automotive": automotive_model,
        "energy": energy_model,
        "agriculture": agriculture_model,
    }
