"""
Smart City Digital Twin Model.

This model represents urban infrastructure including traffic lights, parking,
street lighting, air quality monitoring, public transport, waste management
and emergency response, capturing the heterogeneity typical of smart-city
DTs operated at scale.

Goal: Optimize traffic flow, manage parking availability, reduce energy
consumption, monitor environmental conditions, coordinate public transport
and waste collection, and support emergency response.
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


def create_smart_city_model() -> ERDTModel:
    """
    Create a smart city digital twin model.

    Returns:
        ERDTModel: Complete smart city model
    """
    model = ERDTModel(
        name="Smart City Digital Twin",
        description="Digital twin for urban infrastructure and city management",
        goal="Optimize traffic, parking, energy, public transport, waste collection "
             "and environmental monitoring across the city",
    )

    # -------- Value sets --------
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_location = ValueSet("GeoCoordinates")
    vs_light_state = ValueSet("LightState", "red, yellow, green")
    vs_bool = ValueSet("Boolean")
    vs_route = ValueSet("Route", "Ordered list of GeoCoordinates")
    vs_dt = ValueSet("DateTime")

    # -------- Entity: TrafficLight --------
    traffic_light = Entity("TrafficLight", description="Traffic signal controller")
    traffic_light.add_attribute(Attribute("id", vs_string))
    traffic_light.add_attribute(Attribute("location", vs_location))
    traffic_light.add_attribute(Attribute("current_state", vs_light_state))
    traffic_light.add_attribute(
        HistoricalAttribute("traffic_flow", vs_int, "Vehicles per minute over time")
    )
    traffic_light.add_attribute(
        DerivedAttribute(
            "optimal_timing", vs_int,
            "Optimal signal timing in seconds",
            "Calculated from traffic flow patterns of nearby intersections",
        )
    )
    model.add_entity(traffic_light)

    # -------- Entity: ParkingSpot --------
    parking_spot = Entity("ParkingSpot", description="Parking space")
    parking_spot.add_attribute(Attribute("id", vs_string))
    parking_spot.add_attribute(Attribute("location", vs_location))
    parking_spot.add_attribute(Attribute("occupied", vs_bool))
    parking_spot.add_attribute(
        HistoricalAttribute("occupancy", vs_bool, "Occupancy status over time")
    )
    parking_spot.add_attribute(
        DerivedAttribute(
            "predicted_availability", vs_float,
            "Probability the spot is free in 10 minutes (0–1)",
            "Computed from recent occupancy patterns and time-of-day",
        )
    )
    model.add_entity(parking_spot)

    # -------- Entity: StreetLight --------
    street_light = Entity("StreetLight", description="Street lighting fixture")
    street_light.add_attribute(Attribute("id", vs_string))
    street_light.add_attribute(Attribute("location", vs_location))
    street_light.add_attribute(Attribute("brightness", vs_int, "0–100 percentage"))
    street_light.add_attribute(
        HistoricalAttribute("energy_consumption", vs_float, "kWh over time")
    )
    model.add_entity(street_light)

    # -------- Entity: AirQualitySensor --------
    air_sensor = Entity("AirQualitySensor", description="Environmental monitoring sensor")
    air_sensor.add_attribute(Attribute("id", vs_string))
    air_sensor.add_attribute(Attribute("location", vs_location))
    air_sensor.add_attribute(
        HistoricalAttribute("air_quality_index", vs_int, "AQI value over time")
    )
    air_sensor.add_attribute(
        HistoricalAttribute("pm25", vs_float, "PM2.5 concentration over time")
    )
    air_sensor.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Ambient temperature over time")
    )
    air_sensor.add_attribute(
        HistoricalAttribute("humidity", vs_float, "Relative humidity over time")
    )
    model.add_entity(air_sensor)

    # -------- Entity: BusStop --------
    bus_stop = Entity("BusStop", description="Public-transport stop")
    bus_stop.add_attribute(Attribute("id", vs_string))
    bus_stop.add_attribute(Attribute("location", vs_location))
    bus_stop.add_attribute(Attribute("name", vs_string))
    bus_stop.add_attribute(
        HistoricalAttribute("waiting_passengers", vs_int, "Estimated passengers waiting over time")
    )
    model.add_entity(bus_stop)

    # -------- Entity: PublicBus --------
    public_bus = Entity("PublicBus", description="Public transport vehicle")
    public_bus.add_attribute(Attribute("id", vs_string))
    public_bus.add_attribute(Attribute("line", vs_string, "Bus line identifier"))
    public_bus.add_attribute(
        HistoricalAttribute("location", vs_location, "GPS position over time")
    )
    public_bus.add_attribute(
        HistoricalAttribute("passenger_count", vs_int, "Onboard passengers over time")
    )
    public_bus.add_attribute(
        DerivedAttribute(
            "estimated_arrival", vs_dt,
            "Predicted arrival time at next stop",
            "Computed from current location, traffic flow and historical timings",
        )
    )
    model.add_entity(public_bus)

    # -------- Entity: WasteContainer --------
    waste = Entity("WasteContainer", description="Smart waste container with fill-level sensor")
    waste.add_attribute(Attribute("id", vs_string))
    waste.add_attribute(Attribute("location", vs_location))
    waste.add_attribute(Attribute("waste_type", vs_string, "general / paper / glass / organic"))
    waste.add_attribute(
        HistoricalAttribute("fill_level", vs_float, "Fill percentage (0–100) over time")
    )
    waste.add_attribute(
        DerivedAttribute(
            "needs_collection", vs_bool,
            "Whether the container needs to be collected",
            "True when fill_level > 80% sustained over the last hour",
        )
    )
    model.add_entity(waste)

    # -------- Entity: EmergencyVehicle --------
    emergency = Entity("EmergencyVehicle", description="Ambulance, police car or fire truck")
    emergency.add_attribute(Attribute("id", vs_string))
    emergency.add_attribute(Attribute("kind", vs_string, "ambulance / police / fire"))
    emergency.add_attribute(Attribute("active", vs_bool, "On emergency call"))
    emergency.add_attribute(
        HistoricalAttribute("location", vs_location, "GPS position over time")
    )
    emergency.add_attribute(
        HistoricalAttribute("route", vs_route, "Active route over time")
    )
    model.add_entity(emergency)

    # -------- Relationships --------
    model.add_relationship(Relationship("near", [traffic_light, parking_spot]))
    model.add_relationship(Relationship("illuminates", [street_light, parking_spot]))
    model.add_relationship(Relationship("serves", [public_bus, bus_stop]))
    model.add_relationship(Relationship("monitors_area_of", [air_sensor, bus_stop]))
    model.add_relationship(Relationship("crosses", [emergency, traffic_light]))

    # -------- Interfaces --------
    # TrafficLight interfaces (1Q + 1U + 1A)
    control_traffic_light = Interface(
        "control_traffic_light", traffic_light, InterfaceType.UPDATE,
        "Change traffic light state",
        parameters=["state", "duration"],
        security_constraints=["Requires traffic management system authorization"],
    )
    model.add_interface(control_traffic_light)

    get_traffic_flow = Interface(
        "get_traffic_flow", traffic_light, InterfaceType.QUERY,
        "Read recent traffic flow at this intersection",
        parameters=["since (datetime)"],
        returns="Time-series of vehicle counts",
        security_constraints=["Public API with rate limiting"],
    )
    model.add_interface(get_traffic_flow)

    optimize_corridor = Interface(
        "optimize_corridor_timings", traffic_light, InterfaceType.ANALYTICAL,
        "Compute coordinated green-wave timings along a corridor",
        parameters=["corridor_id"],
        returns="Map of traffic-light id -> timing seconds",
        security_constraints=["Requires traffic management system authorization"],
    )
    model.add_interface(optimize_corridor)

    # ParkingSpot interfaces (2Q)
    get_parking_availability = Interface(
        "get_parking_availability", parking_spot, InterfaceType.QUERY,
        "Get real-time parking availability in area",
        parameters=["area_bounds"],
        returns="List of available parking spots",
        security_constraints=["Public API with rate limiting"],
    )
    model.add_interface(get_parking_availability)

    predict_parking = Interface(
        "predict_parking", parking_spot, InterfaceType.ANALYTICAL,
        "Predict parking availability for an arrival time",
        parameters=["area_bounds", "arrival_time"],
        returns="List of (spot_id, probability)",
        security_constraints=["Public API with rate limiting"],
    )
    model.add_interface(predict_parking)

    # StreetLight interfaces (1U)
    adjust_street_light = Interface(
        "adjust_street_light", street_light, InterfaceType.UPDATE,
        "Adjust street light brightness",
        parameters=["brightness"],
        security_constraints=["Requires energy management authorization"],
    )
    model.add_interface(adjust_street_light)

    # AirQualitySensor interfaces (1Q)
    get_air_quality = Interface(
        "get_air_quality", air_sensor, InterfaceType.QUERY,
        "Get air-quality readings around a location",
        parameters=["area_bounds", "since (datetime)"],
        returns="List of sensor readings",
        security_constraints=["Public API with rate limiting"],
    )
    model.add_interface(get_air_quality)

    # PublicBus interfaces (1Q + 1U)
    set_bus_location = Interface(
        "set_location", public_bus, InterfaceType.UPDATE,
        "Update bus GPS position",
        parameters=["location"],
        security_constraints=["Requires fleet system authentication"],
    )
    model.add_interface(set_bus_location)

    get_eta = Interface(
        "get_eta", public_bus, InterfaceType.QUERY,
        "Get estimated arrival times for a bus line at a stop",
        parameters=["bus_stop_id"],
        returns="Estimated arrival time",
        security_constraints=["Public API"],
    )
    model.add_interface(get_eta)

    # WasteContainer interfaces (1U)
    update_fill_level = Interface(
        "update_fill_level", waste, InterfaceType.UPDATE,
        "Update fill-level reading from container sensor",
        parameters=["fill_level"],
        security_constraints=["Requires container telemetry authentication"],
    )
    model.add_interface(update_fill_level)

    # EmergencyVehicle interfaces (1R + 1U)
    assign_emergency_route = Interface(
        "assign_route", emergency, InterfaceType.RELATIONSHIP,
        "Assign an active route and traffic-light corridor priority",
        parameters=["route", "priority_corridor_id"],
        security_constraints=["Requires emergency dispatcher authorization"],
    )
    model.add_interface(assign_emergency_route)

    set_emergency_location = Interface(
        "set_location", emergency, InterfaceType.UPDATE,
        "Update vehicle GPS position",
        parameters=["location"],
        security_constraints=["Requires emergency fleet authentication"],
    )
    model.add_interface(set_emergency_location)

    # -------- Incoming events --------
    model.add_incoming_event(IncomingEvent(
        "sensor_update", control_traffic_light,
        "Traffic flow sensor data",
        event_source="Traffic monitoring cameras and sensors",
    ))
    model.add_incoming_event(IncomingEvent(
        "parking_status_poll", get_parking_availability,
        "Poll parking spot occupancy sensors",
        event_source="Parking sensors",
    ))
    model.add_incoming_event(IncomingEvent(
        "air_quality_telemetry", get_air_quality,
        "Periodic air-quality readings",
        event_source="Air-quality sensor station",
    ))
    model.add_incoming_event(IncomingEvent(
        "bus_gps_telemetry", set_bus_location,
        "Bus GPS coordinates and passenger count",
        event_source="On-board bus telemetry unit",
    ))
    model.add_incoming_event(IncomingEvent(
        "waste_fill_telemetry", update_fill_level,
        "Fill-level reading from container ultrasonic sensor",
        event_source="Smart waste container",
    ))
    model.add_incoming_event(IncomingEvent(
        "emergency_dispatch", assign_emergency_route,
        "Dispatch event activates emergency response",
        event_source="Emergency dispatch system (112)",
    ))

    # -------- Outgoing events --------
    model.add_outgoing_event(OutgoingEvent(
        "traffic_optimization", control_traffic_light,
        "Optimize traffic light timing based on flow",
        event_target="Traffic light controllers",
        trigger_condition="Traffic flow pattern changes detected",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "dim_lights", adjust_street_light,
        "Reduce street light brightness to save energy",
        event_target="Street light controllers",
        trigger_condition="Low pedestrian activity detected",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "collection_request", update_fill_level,
        "Notify waste-collection fleet that a container needs collection",
        event_target="Waste-collection fleet management system",
        trigger_condition="needs_collection becomes True",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "green_wave_request", optimize_corridor,
        "Request a green wave for an emergency vehicle",
        event_target="Traffic-light controllers along the corridor",
        trigger_condition="Active emergency vehicle approaching corridor",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "air_alert", get_air_quality,
        "Public air-quality alert when AQI exceeds threshold",
        event_target="Public alerting channel and city open-data API",
        trigger_condition="Sustained AQI > 150 for 30 minutes",
    ))

    return model
