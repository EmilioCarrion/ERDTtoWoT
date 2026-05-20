"""
Energy/Utilities Digital Twin Model.

This model represents a distributed power generation and distribution system
including conventional plants, turbines, distributed renewables (solar, wind),
energy storage (batteries), the transmission grid, smart meters and consumers.
The DT supports load balancing, demand prediction, fault detection and
integration of renewable generation.

Goal: Monitor power generation, optimise grid load balancing, predict demand,
integrate renewable energy sources and storage, and detect faults across the
distribution network.
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
        description="Digital twin for power generation, storage and distribution management",
        goal="Optimise grid operations, predict demand, integrate renewables and storage, "
             "and detect faults",
    )

    # -------- Value sets --------
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_bool = ValueSet("Boolean")
    vs_dt = ValueSet("DateTime")
    vs_location = ValueSet("GeoCoordinates")
    vs_plant_type = ValueSet("PlantType", "coal, gas, nuclear, solar, wind, hydro")
    vs_battery_state = ValueSet("BatteryState", "charging, discharging, idle")

    # -------- Entity: PowerPlant --------
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
        DerivedAttribute(
            "efficiency", vs_float,
            "Generation efficiency percentage",
            "Calculated from output vs. fuel consumption (or capacity factor for renewables)",
        )
    )
    model.add_entity(power_plant)

    # -------- Entity: Turbine --------
    turbine = Entity("Turbine", description="Power generation turbine")
    turbine.add_attribute(Attribute("id", vs_string))
    turbine.add_attribute(Attribute("manufacturer", vs_string))
    turbine.add_attribute(
        HistoricalAttribute("rotation_speed", vs_float, "RPM over time")
    )
    turbine.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Operating temperature over time")
    )
    turbine.add_attribute(
        HistoricalAttribute("vibration", vs_float, "Vibration level over time")
    )
    turbine.add_attribute(
        DerivedAttribute(
            "remaining_useful_life_h", vs_float,
            "Remaining useful life estimate in hours",
            "Computed from accumulated wear and vibration trends",
        )
    )
    model.add_entity(turbine)

    # -------- Entity: Grid --------
    grid = Entity("Grid", description="Power distribution grid (region)")
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
        DerivedAttribute(
            "stability_index", vs_float,
            "Grid stability score 0–100",
            "Calculated from voltage, frequency, and load variations",
        )
    )
    model.add_entity(grid)

    # -------- Entity: Consumer --------
    consumer = Entity("Consumer", description="Energy consumer (residential, commercial, industrial)")
    consumer.add_attribute(Attribute("id", vs_string))
    consumer.add_attribute(Attribute("type", vs_string, "residential, commercial, industrial"))
    consumer.add_attribute(Attribute("location", vs_location))
    consumer.add_attribute(
        HistoricalAttribute("consumption", vs_float, "Power consumption in kW over time")
    )
    consumer.add_attribute(
        DerivedAttribute(
            "predicted_demand", vs_float,
            "Predicted demand in kW",
            "ML prediction based on historical patterns and weather forecast",
        )
    )
    model.add_entity(consumer)

    # -------- Entity: SmartMeter --------
    smart_meter = Entity("SmartMeter", description="Smart electricity meter at a consumer site")
    smart_meter.add_attribute(Attribute("id", vs_string))
    smart_meter.add_attribute(Attribute("serial_number", vs_string))
    smart_meter.add_attribute(Attribute("location", vs_location))
    smart_meter.add_attribute(
        HistoricalAttribute("consumption_kwh", vs_float, "Cumulative kWh over time")
    )
    smart_meter.add_attribute(
        HistoricalAttribute("instantaneous_power_kw", vs_float, "kW over time")
    )
    smart_meter.add_attribute(
        HistoricalAttribute("power_factor", vs_float, "Power factor over time")
    )
    model.add_entity(smart_meter)

    # -------- Entity: SolarPanel --------
    solar = Entity("SolarPanel", description="Distributed solar generation array")
    solar.add_attribute(Attribute("id", vs_string))
    solar.add_attribute(Attribute("location", vs_location))
    solar.add_attribute(Attribute("nominal_capacity_kw", vs_float))
    solar.add_attribute(
        HistoricalAttribute("output_kw", vs_float, "Instantaneous output in kW over time")
    )
    solar.add_attribute(
        HistoricalAttribute("irradiance_w_m2", vs_float, "Solar irradiance W/m^2 over time")
    )
    solar.add_attribute(
        DerivedAttribute(
            "performance_ratio", vs_float,
            "Output vs. theoretical from irradiance",
            "output_kw divided by (nominal_capacity_kw * irradiance/1000)",
        )
    )
    model.add_entity(solar)

    # -------- Entity: Battery --------
    battery = Entity("Battery", description="Grid-scale or distributed energy storage unit")
    battery.add_attribute(Attribute("id", vs_string))
    battery.add_attribute(Attribute("location", vs_location))
    battery.add_attribute(Attribute("nominal_capacity_kwh", vs_float))
    battery.add_attribute(Attribute("state", vs_battery_state))
    battery.add_attribute(
        HistoricalAttribute("state_of_charge", vs_float, "SoC percentage 0–100 over time")
    )
    battery.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Cell temperature over time")
    )
    battery.add_attribute(
        DerivedAttribute(
            "state_of_health", vs_float,
            "SoH percentage 0–100",
            "Estimated from cycles, average DoD and impedance trends",
        )
    )
    model.add_entity(battery)

    # -------- Relationships --------
    model.add_relationship(Relationship("powers", [power_plant, grid]))
    model.add_relationship(Relationship("contains", [power_plant, turbine]))
    model.add_relationship(Relationship("supplies", [grid, consumer]))
    model.add_relationship(Relationship("metered_by", [consumer, smart_meter]))
    model.add_relationship(Relationship("injects_into", [solar, grid]))
    model.add_relationship(Relationship("buffers", [battery, grid]))

    # -------- Interfaces --------
    # PowerPlant: 1U
    adjust_output = Interface(
        "adjust_output", power_plant, InterfaceType.UPDATE,
        "Adjust power plant output",
        parameters=["target_output_mw"],
        security_constraints=["Requires grid operator authorization"],
    )
    model.add_interface(adjust_output)

    # Grid: 1Q + 1A
    get_grid_status = Interface(
        "get_grid_status", grid, InterfaceType.QUERY,
        "Get real-time grid status",
        returns="Grid metrics including load, voltage, frequency, stability index",
        security_constraints=["Requires monitoring system access"],
    )
    model.add_interface(get_grid_status)

    detect_fault = Interface(
        "detect_fault", grid, InterfaceType.ANALYTICAL,
        "Detect and locate grid faults from telemetry anomalies",
        parameters=["window_minutes"],
        returns="List of (substation, fault_type, confidence)",
        security_constraints=["Internal SCADA analytics"],
    )
    model.add_interface(detect_fault)

    # Consumer: 1A
    predict_demand = Interface(
        "predict_demand", consumer, InterfaceType.ANALYTICAL,
        "Predict future energy demand",
        parameters=["forecast_hours"],
        returns="Demand forecast",
        security_constraints=["Internal analytics system"],
    )
    model.add_interface(predict_demand)

    # SmartMeter: 1U + 1Q
    push_meter_reading = Interface(
        "push_reading", smart_meter, InterfaceType.UPDATE,
        "Push a meter reading",
        parameters=["consumption_kwh", "instantaneous_power_kw", "power_factor", "timestamp"],
        security_constraints=["Requires meter device authentication"],
    )
    model.add_interface(push_meter_reading)

    get_meter_history = Interface(
        "get_meter_history", smart_meter, InterfaceType.QUERY,
        "Get historical readings for a meter",
        parameters=["since (datetime)"],
        returns="Time-series of consumption_kwh",
        security_constraints=["Requires consumer or utility authentication"],
    )
    model.add_interface(get_meter_history)

    # SolarPanel: 1U
    push_solar_reading = Interface(
        "push_reading", solar, InterfaceType.UPDATE,
        "Push solar inverter telemetry",
        parameters=["output_kw", "irradiance_w_m2", "timestamp"],
        security_constraints=["Requires inverter authentication"],
    )
    model.add_interface(push_solar_reading)

    # Battery: 1U + 1A
    set_battery_state = Interface(
        "set_battery_state", battery, InterfaceType.UPDATE,
        "Command battery to charge/discharge/idle",
        parameters=["state", "power_kw"],
        security_constraints=["Requires grid operator authorization"],
    )
    model.add_interface(set_battery_state)

    optimise_dispatch = Interface(
        "optimise_dispatch", battery, InterfaceType.ANALYTICAL,
        "Compute optimal charge/discharge schedule for next horizon",
        parameters=["horizon_hours", "price_signal"],
        returns="Schedule of (hour, power_kw)",
        security_constraints=["Requires energy management system authorization"],
    )
    model.add_interface(optimise_dispatch)

    # -------- Incoming events --------
    model.add_incoming_event(IncomingEvent(
        "smart_meter_data", push_meter_reading,
        "Real-time consumption from smart meters",
        event_source="Smart meter network",
    ))
    model.add_incoming_event(IncomingEvent(
        "grid_monitoring", get_grid_status,
        "Monitor grid parameters",
        event_source="SCADA system",
    ))
    model.add_incoming_event(IncomingEvent(
        "solar_inverter_telemetry", push_solar_reading,
        "Telemetry from solar inverters",
        event_source="Solar plant inverter",
    ))
    model.add_incoming_event(IncomingEvent(
        "battery_telemetry", set_battery_state,
        "BMS telemetry update for the battery",
        event_source="Battery management system (BMS)",
    ))

    # -------- Outgoing events --------
    model.add_outgoing_event(OutgoingEvent(
        "load_balancing", adjust_output,
        "Adjust generation to balance grid load",
        event_target="Power plant control systems",
        trigger_condition="Grid load imbalance detected or demand forecast changes",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "demand_response", predict_demand,
        "Request consumers to reduce load during peak demand",
        event_target="Consumer demand response systems",
        trigger_condition="Predicted demand exceeds available capacity",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "battery_dispatch", set_battery_state,
        "Send dispatch command to battery (charge/discharge/idle)",
        event_target="Battery management system",
        trigger_condition="Optimal dispatch schedule changes",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "fault_alert", detect_fault,
        "Notify operations team of detected grid fault",
        event_target="Operations control room",
        trigger_condition="Fault detection confidence above threshold",
    ))

    return model
