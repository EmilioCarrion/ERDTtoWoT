# ERDT Testing Framework

Comprehensive testing framework for **Entity-Relationship Digital Twin (ERDT)** conceptual models with automatic transformation to **Web of Things (WoT)** Thing Descriptions.

## Overview

This framework implements the ERDT modeling method for digital twins, providing:

- **Core ERDT model classes** for defining digital twin conceptual models
- **7 industry-specific example models** (logistics, manufacturing, healthcare, smart city, automotive, energy, agriculture)
- **ERDT → WoT transformation** that converts conceptual models to W3C WoT Thing Descriptions
- **Comprehensive test suite** with pytest to validate models and transformations
- **WoT validation** to ensure generated Thing Descriptions comply with W3C standards

## ERDT Modeling Method

The ERDT method extends Entity-Relationship models with digital twin-specific constructs:

### Core Concepts

- **Entities**: Physical or logical components (machines, sensors, vehicles, etc.)
- **Attributes**: Properties of entities
  - **Regular attributes**: Standard properties
  - **Historical attributes**: Time-series data for ML and analysis
  - **Derived attributes**: Computed values (analytics, predictions)
- **Relationships**: Connections between entities
- **Interfaces**: Secure access points for data query/modification
- **Data Flows**:
  - **Incoming Events**: Data from physical → digital (event-based or periodic)
  - **Outgoing Events**: Commands from digital → physical (actuators, alerts)

## Installation

```bash
cd erdt_tests
pip install -r requirements.txt
```

## Usage

### Creating an ERDT Model

```python
from erdt_tests.models.core import (
    ERDTModel, Entity, Attribute, HistoricalAttribute,
    Interface, InterfaceType, IncomingEvent, OutgoingEvent, ValueSet
)

# Create model
model = ERDTModel(
    name="My Digital Twin",
    description="Example DT",
    goal="Monitor and optimize operations"
)

# Define entity
sensor = Entity("TemperatureSensor")
sensor.add_attribute(
    HistoricalAttribute("temperature", ValueSet("Float"), "Temperature in °C")
)
model.add_entity(sensor)

# Define interface
update_temp = Interface(
    "update_temperature",
    sensor,
    InterfaceType.UPDATE,
    "Update sensor reading",
    security_constraints=["Requires IoT device authentication"]
)
model.add_interface(update_temp)

# Define data flow
model.add_incoming_event(IncomingEvent(
    "temperature_reading",
    update_temp,
    "Temperature updates from sensor",
    event_source="IoT temperature sensor"
))
```

### Using Industry Models

```python
from erdt_tests.models.industries.logistics import create_logistics_model
from erdt_tests.models.industries.manufacturing import create_manufacturing_model

# Create pre-built industry model
logistics_dt = create_logistics_model()
print(logistics_dt.summary())
```

### Transforming to WoT

```python
from erdt_tests.transformation.erdt_to_wot import transform_erdt_to_wot
from erdt_tests.validation.wot_validator import validate_wot_thing_description

# Transform ERDT to WoT Thing Descriptions
# Returns a DICT with one TD per entity
wot_tds = transform_erdt_to_wot(logistics_dt)

# wot_tds = {
#   "Hive": {...WoT TD for Hive...},
#   "Picker": {...WoT TD for Picker...},
#   "Truck": {...WoT TD for Truck...},
#   "Driver": {...WoT TD for Driver...}
# }

# Validate each entity's WoT TD
for entity_name, wot_td in wot_tds.items():
    is_valid, messages = validate_wot_thing_description(wot_td)
    print(f"{entity_name}: Valid={is_valid}")
    if messages:
        for msg in messages:
            print(f"  {msg}")
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific industry tests
pytest tests/test_logistics.py -v
pytest tests/test_manufacturing.py -v

# Run only core model tests
pytest tests/test_core_models.py -v
```

## Industry Models

### 1. Logistics (Case Study from ERDT Paper)

Online grocery delivery with warehouses, pickers, trucks, and drivers.

**Goal**: Worker location tracking, LEZ violation alerts, route analysis

**Entities**: Hive, Picker, Truck, Driver

**Key Features**:
- Indoor location tracking for warehouse workers
- GPS tracking for delivery vehicles
- Automatic alerts when trucks enter low-emission zones
- Historical route analysis

```python
from erdt_tests.models.industries.logistics import create_logistics_model
model = create_logistics_model()
```

### 2. Manufacturing

Production line with machines, sensors, and predictive maintenance.

**Goal**: Process monitoring, failure prediction, efficiency optimization

**Key Features**:
- Real-time sensor telemetry (temperature, vibration)
- ML-based failure probability prediction
- Automated maintenance scheduling

### 3. Healthcare

Patient monitoring with medical devices and vital signs.

**Goal**: Personalized treatment, emergency response

**Key Features**:
- Continuous vital signs monitoring (heart rate, BP, SpO2)
- HIPAA-compliant security
- Emergency alert system

### 4. Smart City

Urban infrastructure (traffic, parking, lighting, air quality).

**Goal**: Traffic optimization, energy management, environmental monitoring

**Key Features**:
- Traffic flow optimization
- Real-time parking availability
- Adaptive street lighting for energy savings

### 5. Automotive

Connected vehicle with diagnostics and safety features.

**Goal**: Vehicle health monitoring, driver safety, diagnostics

**Key Features**:
- OBD-II telemetry
- Battery monitoring and range estimation
- Safety alerts and maintenance reminders

### 6. Energy

Power generation and distribution grid management.

**Goal**: Load balancing, demand prediction, renewable integration

**Key Features**:
- Real-time grid monitoring
- ML-based demand forecasting
- Automated load balancing

### 7. Agriculture

Precision farming with fields, crops, irrigation, and weather.

**Goal**: Yield optimization, resource management, soil health

**Key Features**:
- Soil moisture and nutrient monitoring
- Automated irrigation control
- ML-based yield prediction

## ERDT to WoT Transformation

**IMPORTANT**: The transformation creates **ONE Thing Description per ERDT Entity**.

Each entity becomes an independent WoT Thing with its own properties, actions, and events.

| ERDT Concept | WoT Mapping |
|--------------|-------------|
| **Entity** | **WoT Thing** (one TD per entity) |
| Attributes | Properties (of that entity's TD) |
| Historical Attributes | Properties (observable: true) |
| Derived Attributes | Properties (readOnly: true) |
| Interfaces (Query) | Properties (readable) |
| Interfaces (Update/Analytical) | Actions (of the entity's TD) |
| Incoming Events | Actions (invokable, for target entity) |
| Outgoing Events | Events (of the source entity's TD) |
| Relationships | Links between TDs |

### Example

For the logistics model with 4 entities (Hive, Picker, Truck, Driver), the transformation generates:

- `Hive` Thing Description
- `Picker` Thing Description  
- `Truck` Thing Description
- `Driver` Thing Description

Each TD is independent and can be deployed/discovered separately.

## Project Structure

```
erdt_tests/
├── models/
│   ├── core.py                 # Core ERDT classes
│   └── industries/             # Industry-specific models
│       ├── logistics.py
│       ├── manufacturing.py
│       ├── healthcare.py
│       ├── smart_city.py
│       ├── automotive.py
│       ├── energy.py
│       └── agriculture.py
├── transformation/
│   └── erdt_to_wot.py         # ERDT → WoT transformation
├── validation/
│   └── wot_validator.py       # WoT TD validator
├── tests/
│   ├── conftest.py            # Pytest fixtures
│   ├── test_core_models.py    # Core model tests
│   └── test_*.py              # Industry model tests
├── requirements.txt
├── pytest.ini
└── README.md
```

## Key Differences from Original ERDT Paper

**DataRequest Deprecated**: The original paper included `DataRequest` as a separate data flow type for periodic polling. In this implementation, we use only `IncomingEvent` for all data flows from physical to digital, regardless of whether they are event-based or periodic. This simplification reflects that at the conceptual level, we only care that an event arrives, not the implementation details of how it's triggered.

## References

- **ERDT Paper**: "Conceptual modelling method for digital twins" by Emilio Carrión, Óscar Pastor, and Pedro Valderas
- **W3C WoT**: https://www.w3.org/TR/wot-thing-description/

## License

This testing framework is provided for research and educational purposes.
