"""
Automotive Digital Twin Model.

This model represents a connected vehicle including engine (or e-motor),
battery, tire-pressure monitoring, charging infrastructure, ADAS sensors,
and the driver. The DT supports diagnostics, driver safety, ADAS coordination,
and electric-vehicle charging optimisation.

Goal: Monitor vehicle health, provide diagnostics, ensure driver safety,
support ADAS features, and coordinate EV charging.
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
        description="Digital twin for connected vehicle monitoring, ADAS and EV charging",
        goal="Monitor vehicle health, diagnostics, safety, ADAS features and charging",
    )

    # -------- Value sets --------
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_bool = ValueSet("Boolean")
    vs_dt = ValueSet("DateTime")
    vs_location = ValueSet("GeoCoordinates")
    vs_driving_mode = ValueSet("DrivingMode", "manual, cruise, autonomous")
    vs_charging_state = ValueSet("ChargingState", "idle, charging, fast_charging, complete, error")

    # -------- Entity: Vehicle --------
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
    vehicle.add_attribute(
        HistoricalAttribute("acceleration", vs_float, "Longitudinal acceleration m/s^2 over time")
    )
    model.add_entity(vehicle)

    # -------- Entity: Engine --------
    engine = Entity("Engine", description="Vehicle engine (ICE or e-motor)")
    engine.add_attribute(Attribute("id", vs_string))
    engine.add_attribute(Attribute("kind", vs_string, "ice, hybrid, electric"))
    engine.add_attribute(
        HistoricalAttribute("rpm", vs_int, "Revolutions per minute over time")
    )
    engine.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Engine temperature over time")
    )
    engine.add_attribute(
        HistoricalAttribute("fuel_consumption", vs_float, "L/100km or kWh/100km over time")
    )
    engine.add_attribute(
        DerivedAttribute(
            "health_score", vs_float,
            "Engine health 0–100",
            "Calculated from temperature, vibration and performance metrics",
        )
    )
    model.add_entity(engine)

    # -------- Entity: Battery --------
    battery = Entity("Battery", description="Vehicle battery (12V starter or HV traction)")
    battery.add_attribute(Attribute("id", vs_string))
    battery.add_attribute(Attribute("kind", vs_string, "12v_starter, hv_traction"))
    battery.add_attribute(Attribute("nominal_capacity_kwh", vs_float))
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
        DerivedAttribute(
            "range_estimate_km", vs_float,
            "Estimated remaining range in km",
            "Calculated from charge level, ambient temperature and recent consumption",
        )
    )
    battery.add_attribute(
        DerivedAttribute(
            "state_of_health", vs_float,
            "Battery SoH percentage 0–100",
            "Estimated from cycles, average DoD and impedance trends",
        )
    )
    model.add_entity(battery)

    # -------- Entity: Tire --------
    tire = Entity("Tire", description="Wheel tire with pressure/temperature sensor")
    tire.add_attribute(Attribute("id", vs_string))
    tire.add_attribute(Attribute("position", vs_string, "FL, FR, RL, RR"))
    tire.add_attribute(
        HistoricalAttribute("pressure_bar", vs_float, "Tire pressure over time")
    )
    tire.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Tire temperature over time")
    )
    tire.add_attribute(
        DerivedAttribute(
            "wear_estimate", vs_float,
            "Wear percentage 0–100",
            "Estimated from cumulative km, hard braking events and pressure deviations",
        )
    )
    model.add_entity(tire)

    # -------- Entity: ADASModule --------
    adas = Entity("ADASModule", description="Advanced driver-assistance system module")
    adas.add_attribute(Attribute("id", vs_string))
    adas.add_attribute(Attribute("software_version", vs_string))
    adas.add_attribute(Attribute("lane_keeping_active", vs_bool))
    adas.add_attribute(Attribute("acc_active", vs_bool, "Adaptive cruise control engaged"))
    adas.add_attribute(
        HistoricalAttribute("front_distance_m", vs_float, "Distance to front vehicle over time")
    )
    adas.add_attribute(
        HistoricalAttribute("ttc_seconds", vs_float, "Time-to-collision over time")
    )
    model.add_entity(adas)

    # -------- Entity: ChargingStation --------
    charger = Entity("ChargingStation", description="EV charging point")
    charger.add_attribute(Attribute("id", vs_string))
    charger.add_attribute(Attribute("location", vs_location))
    charger.add_attribute(Attribute("connector_type", vs_string, "Type2, CCS, CHAdeMO"))
    charger.add_attribute(Attribute("max_power_kw", vs_float))
    charger.add_attribute(Attribute("state", vs_charging_state))
    charger.add_attribute(
        HistoricalAttribute("delivered_power_kw", vs_float, "Instantaneous delivered power over time")
    )
    model.add_entity(charger)

    # -------- Entity: Driver --------
    driver = Entity("Driver", description="Vehicle driver")
    driver.add_attribute(Attribute("id", vs_string))
    driver.add_attribute(Attribute("name", vs_string))
    driver.add_attribute(Attribute("driving_mode", vs_driving_mode))
    driver.add_attribute(
        HistoricalAttribute("attention_score", vs_float, "Driver-monitor attention 0–100 over time")
    )
    model.add_entity(driver)

    # -------- Relationships --------
    model.add_relationship(Relationship("has_engine", [vehicle, engine]))
    model.add_relationship(Relationship("has_battery", [vehicle, battery]))
    model.add_relationship(Relationship("has_tire", [vehicle, tire]))
    model.add_relationship(Relationship("has_adas", [vehicle, adas]))
    model.add_relationship(Relationship("driven_by", [vehicle, driver]))
    model.add_relationship(Relationship("plugged_into", [vehicle, charger]))

    # -------- Interfaces --------
    # Vehicle: 1Q + 1U
    get_diagnostics = Interface(
        "get_diagnostics", vehicle, InterfaceType.QUERY,
        "Get comprehensive vehicle diagnostics",
        returns="Diagnostic report with all system statuses",
        security_constraints=["Requires vehicle owner or authorised mechanic"],
    )
    model.add_interface(get_diagnostics)

    set_vehicle_location = Interface(
        "set_location", vehicle, InterfaceType.UPDATE,
        "Update vehicle GPS location and speed",
        parameters=["location", "speed", "timestamp"],
        security_constraints=["Requires vehicle telemetry authentication"],
    )
    model.add_interface(set_vehicle_location)

    # Driver: 1U + 1A
    set_driving_mode = Interface(
        "set_driving_mode", driver, InterfaceType.UPDATE,
        "Change driving mode",
        parameters=["mode"],
        security_constraints=["Requires driver authentication"],
    )
    model.add_interface(set_driving_mode)

    alert_driver = Interface(
        "alert_driver", driver, InterfaceType.ANALYTICAL,
        "Alert driver of safety or maintenance issues",
        parameters=["alert_type", "severity", "message"],
        security_constraints=["Automated safety system"],
    )
    model.add_interface(alert_driver)

    # Tire: 1U
    push_tire_reading = Interface(
        "push_reading", tire, InterfaceType.UPDATE,
        "Push tire pressure/temperature reading",
        parameters=["pressure_bar", "temperature", "timestamp"],
        security_constraints=["Requires TPMS authentication"],
    )
    model.add_interface(push_tire_reading)

    # ADAS: 1Q + 1U
    set_adas_state = Interface(
        "set_state", adas, InterfaceType.UPDATE,
        "Enable/disable ADAS subsystems",
        parameters=["lane_keeping_active", "acc_active"],
        security_constraints=["Requires driver authentication"],
    )
    model.add_interface(set_adas_state)

    get_adas_telemetry = Interface(
        "get_telemetry", adas, InterfaceType.QUERY,
        "Read recent ADAS telemetry",
        parameters=["since (datetime)"],
        returns="Time-series of front_distance and ttc",
        security_constraints=["Requires authorised diagnostic tool"],
    )
    model.add_interface(get_adas_telemetry)

    # ChargingStation: 1R + 1A
    start_charging_session = Interface(
        "start_session", charger, InterfaceType.RELATIONSHIP,
        "Start a charging session linking a vehicle to this charger",
        parameters=["vin", "max_power_kw"],
        security_constraints=["Requires e-mobility authentication (RFID/Plug&Charge)"],
    )
    model.add_interface(start_charging_session)

    optimise_charging = Interface(
        "optimise_session", charger, InterfaceType.ANALYTICAL,
        "Optimise charging power profile to minimise cost while meeting target SoC",
        parameters=["target_soc", "leave_time", "price_signal"],
        returns="Power profile (time, kw)",
        security_constraints=["Requires e-mobility authentication"],
    )
    model.add_interface(optimise_charging)

    # -------- Incoming events --------
    model.add_incoming_event(IncomingEvent(
        "obd_telemetry", get_diagnostics,
        "Real-time OBD-II / CAN-bus diagnostic data",
        event_source="Vehicle OBD-II port",
    ))
    model.add_incoming_event(IncomingEvent(
        "battery_monitoring", get_diagnostics,
        "Monitor battery status",
        event_source="Battery management system",
    ))
    model.add_incoming_event(IncomingEvent(
        "tpms_telemetry", push_tire_reading,
        "Tire-pressure monitoring system reading",
        event_source="TPMS sensors",
    ))
    model.add_incoming_event(IncomingEvent(
        "vehicle_gps", set_vehicle_location,
        "Periodic GPS update from the vehicle",
        event_source="In-car GPS",
    ))
    model.add_incoming_event(IncomingEvent(
        "charging_session_started", start_charging_session,
        "Charging session begins when driver plugs in and authenticates",
        event_source="Charging station",
    ))

    # -------- Outgoing events --------
    model.add_outgoing_event(OutgoingEvent(
        "safety_alert", alert_driver,
        "Critical safety alert (e.g., max RPM reached, low battery)",
        event_target="Driver dashboard and mobile app",
        trigger_condition="Safety threshold exceeded",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "maintenance_reminder", alert_driver,
        "Scheduled maintenance reminder",
        event_target="Driver mobile app",
        trigger_condition="Mileage or time-based maintenance due",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "tpms_warning", push_tire_reading,
        "Notify driver of out-of-range tire pressure",
        event_target="Driver dashboard",
        trigger_condition="Tire pressure deviates > 15% from target",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "aeb_request", set_adas_state,
        "Request automatic emergency braking",
        event_target="Brake controller",
        trigger_condition="Time-to-collision below safety threshold",
    ))

    return model
