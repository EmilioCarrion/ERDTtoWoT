"""
Energy/Utilities Digital Twin Model.

This model represents power generation and distribution infrastructure for
grid management, demand prediction, and renewable energy optimization.

Goal: Monitor power generation, optimize grid load balancing, predict demand,
and integrate renewable energy sources.
"""

from ..core import (
    ERDTModel,
    Entity,
    Attribute,
    HistoricalAttribute,
    DerivedAttribute,
    Relationship,
    Interface,
    InterfaceType,
    IncomingEvent,
    OutgoingEvent,
    ValueSet,
)


def create_energy_model() -> ERDTModel:
    """
    Create an energy/utilities digital twin model.
    
    Returns:
        ERDTModel: Complete energy model
    """
    model = ERDTModel(
        name="Energy Digital Twin",
        description="Digital twin for power generation and distribution management",
        goal="Optimize grid operations, predict demand, and integrate renewables"
    )
    
    # Value sets
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_location = ValueSet("GeoCoordinates")
    vs_plant_type = ValueSet("PlantType", "coal, gas, nuclear, solar, wind, hydro")
    
    # Entity: PowerPlant
    power_plant = Entity("PowerPlant", description="Power generation facility")
    power_plant.add_attribute(Attribute("id", vs_string))
    power_plant.add_attribute(Attribute("name", vs_string))
    power_plant.add_attribute(Attribute("type", vs_plant_type))
    power_plant.add_attribute(Attribute("location", vs_location))
    power_plant.add_attribute(Attribute("capacity_mw", vs_float, "Maximum capacity in MW"))
    power_plant.add_attribute(
        HistoricalAttribute("power_output", vs_float, "Current output in MW over time")
    )
    power_plant.add_attribute(
        DerivedAttribute("efficiency", vs_float, "Generation efficiency percentage",
                        "Calculated from output vs. fuel consumption")
    )
    model.add_entity(power_plant)
    
    # Entity: Turbine
    turbine = Entity("Turbine", description="Power generation turbine")
    turbine.add_attribute(Attribute("id", vs_string))
    turbine.add_attribute(
        HistoricalAttribute("rotation_speed", vs_float, "RPM over time")
    )
    turbine.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Operating temperature over time")
    )
    turbine.add_attribute(
        HistoricalAttribute("vibration", vs_float, "Vibration level over time")
    )
    model.add_entity(turbine)
    
    # Entity: Grid
    grid = Entity("Grid", description="Power distribution grid")
    grid.add_attribute(Attribute("id", vs_string))
    grid.add_attribute(Attribute("region", vs_string))
    grid.add_attribute(
        HistoricalAttribute("load", vs_float, "Current load in MW over time")
    )
    grid.add_attribute(
        HistoricalAttribute("voltage", vs_float, "Grid voltage over time")
    )
    grid.add_attribute(
        HistoricalAttribute("frequency", vs_float, "Grid frequency in Hz over time")
    )
    grid.add_attribute(
        DerivedAttribute("stability_index", vs_float, "Grid stability score 0-100",
                        "Calculated from voltage, frequency, and load variations")
    )
    model.add_entity(grid)
    
    # Entity: Consumer
    consumer = Entity("Consumer", description="Energy consumer (residential, commercial, industrial)")
    consumer.add_attribute(Attribute("id", vs_string))
    consumer.add_attribute(Attribute("type", vs_string))
    consumer.add_attribute(Attribute("location", vs_location))
    consumer.add_attribute(
        HistoricalAttribute("consumption", vs_float, "Power consumption in kW over time")
    )
    consumer.add_attribute(
        DerivedAttribute("predicted_demand", vs_float, "Predicted demand in kW",
                        "ML prediction based on historical patterns and weather")
    )
    model.add_entity(consumer)
    
    # Relationships
    model.add_relationship(Relationship("powers", [power_plant, grid]))
    model.add_relationship(Relationship("contains", [power_plant, turbine]))
    model.add_relationship(Relationship("supplies", [grid, consumer]))
    
    # Interfaces
    adjust_output = Interface(
        "adjust_output", power_plant, InterfaceType.UPDATE,
        "Adjust power plant output",
        parameters=["target_output_mw"],
        security_constraints=["Requires grid operator authorization"]
    )
    model.add_interface(adjust_output)
    
    get_grid_status = Interface(
        "get_grid_status", grid, InterfaceType.QUERY,
        "Get real-time grid status",
        returns="Grid metrics including load, voltage, frequency",
        security_constraints=["Requires monitoring system access"]
    )
    model.add_interface(get_grid_status)
    
    predict_demand = Interface(
        "predict_demand", consumer, InterfaceType.ANALYTICAL,
        "Predict future energy demand",
        parameters=["forecast_hours"],
        returns="Demand forecast",
        security_constraints=["Internal analytics system"]
    )
    model.add_interface(predict_demand)
    
    # Data flows
    model.add_incoming_event(IncomingEvent(
        "smart_meter_data", get_grid_status,
        "Real-time consumption from smart meters",
        event_source="Smart meter network",
    ))
    
    model.add_incoming_event(IncomingEvent(
        "grid_monitoring", get_grid_status,
        "Monitor grid parameters",
        event_source="SCADA system",
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "load_balancing", adjust_output,
        "Adjust generation to balance grid load",
        event_target="Power plant control systems",
        trigger_condition="Grid load imbalance detected or demand forecast changes"
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "demand_response", predict_demand,
        "Request consumers to reduce load during peak demand",
        event_target="Consumer demand response systems",
        trigger_condition="Predicted demand exceeds available capacity"
    ))
    
    return model
