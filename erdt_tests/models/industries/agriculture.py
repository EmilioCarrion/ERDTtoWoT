"""
Agriculture Digital Twin Model.

This model represents precision agriculture with fields, crops, irrigation,
and weather monitoring for yield optimization and resource management.

Goal: Optimize crop yields, manage irrigation efficiently, monitor soil health,
and predict harvest outcomes.
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


def create_agriculture_model() -> ERDTModel:
    """
    Create an agriculture digital twin model.
    
    Returns:
        ERDTModel: Complete agriculture model
    """
    model = ERDTModel(
        name="Agriculture Digital Twin",
        description="Digital twin for precision agriculture and farm management",
        goal="Optimize yields, manage irrigation, monitor soil, and predict harvests"
    )
    
    # Value sets
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_location = ValueSet("GeoCoordinates")
    vs_crop_stage = ValueSet("CropStage", "planted, germination, vegetative, flowering, fruiting, harvest")
    vs_bool = ValueSet("Boolean")
    
    # Entity: Field
    field = Entity("Field", description="Agricultural field")
    field.add_attribute(Attribute("id", vs_string))
    field.add_attribute(Attribute("name", vs_string))
    field.add_attribute(Attribute("location", vs_location))
    field.add_attribute(Attribute("area_hectares", vs_float))
    field.add_attribute(
        HistoricalAttribute("soil_moisture", vs_float, "Soil moisture percentage over time")
    )
    field.add_attribute(
        HistoricalAttribute("soil_ph", vs_float, "Soil pH level over time")
    )
    field.add_attribute(
        HistoricalAttribute("soil_nutrients", vs_string, "NPK levels over time")
    )
    model.add_entity(field)
    
    # Entity: Crop
    crop = Entity("Crop", description="Crop being grown")
    crop.add_attribute(Attribute("id", vs_string))
    crop.add_attribute(Attribute("type", vs_string, "wheat, corn, soybeans, etc."))
    crop.add_attribute(Attribute("planting_date", vs_string))
    crop.add_attribute(Attribute("growth_stage", vs_crop_stage))
    crop.add_attribute(
        HistoricalAttribute("height", vs_float, "Average plant height in cm over time")
    )
    crop.add_attribute(
        HistoricalAttribute("health_index", vs_float, "Crop health score 0-100 over time")
    )
    crop.add_attribute(
        DerivedAttribute("predicted_yield", vs_float, "Predicted yield in tons/hectare",
                        "ML prediction based on growth patterns, weather, and soil conditions")
    )
    crop.add_attribute(
        DerivedAttribute("harvest_date", vs_string, "Estimated harvest date",
                        "Calculated from growth stage and weather forecast")
    )
    model.add_entity(crop)
    
    # Entity: IrrigationSystem
    irrigation = Entity("IrrigationSystem", description="Automated irrigation system")
    irrigation.add_attribute(Attribute("id", vs_string))
    irrigation.add_attribute(Attribute("type", vs_string, "drip, sprinkler, pivot"))
    irrigation.add_attribute(Attribute("active", vs_bool))
    irrigation.add_attribute(
        HistoricalAttribute("water_flow", vs_float, "Liters per minute over time")
    )
    irrigation.add_attribute(
        HistoricalAttribute("water_usage", vs_float, "Total liters used over time")
    )
    model.add_entity(irrigation)
    
    # Entity: WeatherStation
    weather = Entity("WeatherStation", description="On-farm weather monitoring")
    weather.add_attribute(Attribute("id", vs_string))
    weather.add_attribute(Attribute("location", vs_location))
    weather.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Temperature in Celsius over time")
    )
    weather.add_attribute(
        HistoricalAttribute("humidity", vs_float, "Relative humidity percentage over time")
    )
    weather.add_attribute(
        HistoricalAttribute("rainfall", vs_float, "Rainfall in mm over time")
    )
    weather.add_attribute(
        HistoricalAttribute("wind_speed", vs_float, "Wind speed in km/h over time")
    )
    weather.add_attribute(
        HistoricalAttribute("solar_radiation", vs_float, "Solar radiation in W/m² over time")
    )
    model.add_entity(weather)
    
    # Relationships
    model.add_relationship(Relationship("planted_in", [crop, field]))
    model.add_relationship(Relationship("irrigates", [irrigation, field]))
    model.add_relationship(Relationship("monitors", [weather, field]))
    
    # Interfaces
    control_irrigation = Interface(
        "control_irrigation", irrigation, InterfaceType.UPDATE,
        "Control irrigation system",
        parameters=["active", "flow_rate"],
        security_constraints=["Requires farm manager authorization"]
    )
    model.add_interface(control_irrigation)
    
    get_field_status = Interface(
        "get_field_status", field, InterfaceType.QUERY,
        "Get comprehensive field status",
        returns="Soil conditions, moisture, nutrients",
        security_constraints=["Requires farm access"]
    )
    model.add_interface(get_field_status)
    
    predict_yield = Interface(
        "predict_yield", crop, InterfaceType.ANALYTICAL,
        "Predict crop yield",
        parameters=["field_id"],
        returns="Yield prediction with confidence interval",
        security_constraints=["Internal analytics system"]
    )
    model.add_interface(predict_yield)
    
    # Data flows
    model.add_incoming_event(IncomingEvent(
        "sensor_data", get_field_status,
        "Soil and environmental sensor data",
        event_source="IoT soil sensors and field monitors",
    ))
    
    model.add_incoming_event(IncomingEvent(
        "weather_update", get_field_status,
        "Fetch weather station data",
        event_source="Weather station",
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "irrigation_command", control_irrigation,
        "Activate irrigation based on soil moisture",
        event_target="Irrigation controller",
        trigger_condition="Soil moisture below threshold and no rain forecast"
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "pest_alert", predict_yield,
        "Alert farmer of potential pest or disease issues",
        event_target="Farm management mobile app",
        trigger_condition="Crop health index drops significantly"
    ))
    
    return model
