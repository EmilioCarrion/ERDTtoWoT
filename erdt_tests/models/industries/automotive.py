"""
Automotive Digital Twin Model.

This model represents a vehicle with engine, battery, and driver monitoring
for diagnostics, safety, and autonomous driving support.

Goal: Monitor vehicle health, provide diagnostics, ensure driver safety,
and support autonomous driving features.
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


def create_automotive_model() -> ERDTModel:
    """
    Create an automotive digital twin model.
    
    Returns:
        ERDTModel: Complete automotive model
    """
    model = ERDTModel(
        name="Automotive Digital Twin",
        description="Digital twin for connected vehicle monitoring and control",
        goal="Monitor vehicle health, diagnostics, safety, and autonomous features"
    )
    
    # Value sets
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_location = ValueSet("GeoCoordinates")
    vs_driving_mode = ValueSet("DrivingMode", "manual, cruise, autonomous")
    
    # Entity: Vehicle
    vehicle = Entity("Vehicle", description="Connected vehicle")
    vehicle.add_attribute(Attribute("vin", vs_string, "Vehicle identification number"))
    vehicle.add_attribute(Attribute("make", vs_string))
    vehicle.add_attribute(Attribute("model", vs_string))
    vehicle.add_attribute(Attribute("year", vs_int))
    vehicle.add_attribute(
        HistoricalAttribute("location", vs_location, "GPS coordinates over time")
    )
    vehicle.add_attribute(
        HistoricalAttribute("speed", vs_float, "Speed in km/h over time")
    )
    model.add_entity(vehicle)
    
    # Entity: Engine
    engine = Entity("Engine", description="Vehicle engine")
    engine.add_attribute(Attribute("id", vs_string))
    engine.add_attribute(
        HistoricalAttribute("rpm", vs_int, "Revolutions per minute over time")
    )
    engine.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Engine temperature over time")
    )
    engine.add_attribute(
        HistoricalAttribute("fuel_consumption", vs_float, "L/100km over time")
    )
    engine.add_attribute(
        DerivedAttribute("health_score", vs_float, "Engine health 0-100",
                        "Calculated from temperature, vibration, and performance metrics")
    )
    model.add_entity(engine)
    
    # Entity: Battery
    battery = Entity("Battery", description="Vehicle battery (electric or hybrid)")
    battery.add_attribute(Attribute("id", vs_string))
    battery.add_attribute(
        HistoricalAttribute("charge_level", vs_float, "Battery percentage over time")
    )
    battery.add_attribute(
        HistoricalAttribute("voltage", vs_float, "Voltage over time")
    )
    battery.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Battery temperature over time")
    )
    battery.add_attribute(
        DerivedAttribute("range_estimate", vs_float, "Estimated range in km",
                        "Calculated from charge level and consumption patterns")
    )
    model.add_entity(battery)
    
    # Entity: Driver
    driver = Entity("Driver", description="Vehicle driver")
    driver.add_attribute(Attribute("id", vs_string))
    driver.add_attribute(Attribute("name", vs_string))
    driver.add_attribute(Attribute("driving_mode", vs_driving_mode))
    model.add_entity(driver)
    
    # Relationships
    model.add_relationship(Relationship("has_engine", [vehicle, engine]))
    model.add_relationship(Relationship("has_battery", [vehicle, battery]))
    model.add_relationship(Relationship("driven_by", [vehicle, driver]))
    
    # Interfaces
    get_diagnostics = Interface(
        "get_diagnostics", vehicle, InterfaceType.QUERY,
        "Get comprehensive vehicle diagnostics",
        returns="Diagnostic report with all system statuses",
        security_constraints=["Requires vehicle owner or authorized mechanic"]
    )
    model.add_interface(get_diagnostics)
    
    set_driving_mode = Interface(
        "set_driving_mode", driver, InterfaceType.UPDATE,
        "Change driving mode",
        parameters=["mode"],
        security_constraints=["Requires driver authentication"]
    )
    model.add_interface(set_driving_mode)
    
    alert_driver = Interface(
        "alert_driver", driver, InterfaceType.ANALYTICAL,
        "Alert driver of safety or maintenance issues",
        parameters=["alert_type", "severity", "message"],
        security_constraints=["Automated safety system"]
    )
    model.add_interface(alert_driver)
    
    # Data flows
    model.add_incoming_event(IncomingEvent(
        "obd_telemetry", get_diagnostics,
        "Real-time OBD-II diagnostic data",
        event_source="Vehicle OBD-II port",
    ))
    
    model.add_incoming_event(IncomingEvent(
        "battery_monitoring", get_diagnostics,
        "Monitor battery status",
        event_source="Battery management system",
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "safety_alert", alert_driver,
        "Critical safety alert (e.g., max RPM reached, low battery)",
        event_target="Driver dashboard and mobile app",
        trigger_condition="Safety threshold exceeded"
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "maintenance_reminder", alert_driver,
        "Scheduled maintenance reminder",
        event_target="Driver mobile app",
        trigger_condition="Mileage or time-based maintenance due"
    ))
    
    return model
