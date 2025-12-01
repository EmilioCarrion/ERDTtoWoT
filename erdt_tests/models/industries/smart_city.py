"""
Smart City Digital Twin Model.

This model represents urban infrastructure including traffic lights, parking,
street lighting, and air quality monitoring for city optimization.

Goal: Optimize traffic flow, manage parking availability, reduce energy consumption,
and monitor environmental conditions.
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
        goal="Optimize traffic, parking, energy, and environmental monitoring"
    )
    
    # Value sets
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_location = ValueSet("GeoCoordinates")
    vs_light_state = ValueSet("LightState", "red, yellow, green")
    vs_bool = ValueSet("Boolean")
    
    # Entity: TrafficLight
    traffic_light = Entity("TrafficLight", description="Traffic signal controller")
    traffic_light.add_attribute(Attribute("id", vs_string))
    traffic_light.add_attribute(Attribute("location", vs_location))
    traffic_light.add_attribute(Attribute("current_state", vs_light_state))
    traffic_light.add_attribute(
        HistoricalAttribute("traffic_flow", vs_int, "Vehicles per minute over time")
    )
    traffic_light.add_attribute(
        DerivedAttribute("optimal_timing", vs_int, "Optimal signal timing in seconds",
                        "Calculated from traffic flow patterns")
    )
    model.add_entity(traffic_light)
    
    # Entity: ParkingSpot
    parking_spot = Entity("ParkingSpot", description="Parking space")
    parking_spot.add_attribute(Attribute("id", vs_string))
    parking_spot.add_attribute(Attribute("location", vs_location))
    parking_spot.add_attribute(Attribute("occupied", vs_bool))
    parking_spot.add_attribute(
        HistoricalAttribute("occupancy", vs_bool, "Occupancy status over time")
    )
    model.add_entity(parking_spot)
    
    # Entity: StreetLight
    street_light = Entity("StreetLight", description="Street lighting fixture")
    street_light.add_attribute(Attribute("id", vs_string))
    street_light.add_attribute(Attribute("location", vs_location))
    street_light.add_attribute(Attribute("brightness", vs_int, "0-100 percentage"))
    street_light.add_attribute(
        HistoricalAttribute("energy_consumption", vs_float, "kWh over time")
    )
    model.add_entity(street_light)
    
    # Entity: AirQualitySensor
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
    model.add_entity(air_sensor)
    
    # Relationships
    model.add_relationship(Relationship("near", [traffic_light, parking_spot]))
    model.add_relationship(Relationship("illuminates", [street_light, parking_spot]))
    
    # Interfaces
    control_traffic_light = Interface(
        "control_traffic_light", traffic_light, InterfaceType.UPDATE,
        "Change traffic light state",
        parameters=["state", "duration"],
        security_constraints=["Requires traffic management system authorization"]
    )
    model.add_interface(control_traffic_light)
    
    get_parking_availability = Interface(
        "get_parking_availability", parking_spot, InterfaceType.QUERY,
        "Get real-time parking availability in area",
        parameters=["area_bounds"],
        returns="List of available parking spots",
        security_constraints=["Public API with rate limiting"]
    )
    model.add_interface(get_parking_availability)
    
    adjust_street_light = Interface(
        "adjust_street_light", street_light, InterfaceType.UPDATE,
        "Adjust street light brightness",
        parameters=["brightness"],
        security_constraints=["Requires energy management authorization"]
    )
    model.add_interface(adjust_street_light)
    
    # Data flows
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
    
    model.add_outgoing_event(OutgoingEvent(
        "traffic_optimization", control_traffic_light,
        "Optimize traffic light timing based on flow",
        event_target="Traffic light controllers",
        trigger_condition="Traffic flow pattern changes detected"
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "dim_lights", adjust_street_light,
        "Reduce street light brightness to save energy",
        event_target="Street light controllers",
        trigger_condition="Low pedestrian activity detected"
    ))
    
    return model
