"""
Agriculture Digital Twin Model.

This model represents a precision-agriculture deployment including fields,
crops, irrigation systems, weather stations, soil sensors, greenhouses and
agricultural machinery. The DT supports yield optimisation, irrigation
scheduling, soil monitoring, harvest planning and machinery coordination.

Goal: Optimise crop yields, manage irrigation efficiently, monitor soil
health, predict harvests, control greenhouse climate and coordinate
agricultural machinery.
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
        goal="Optimise yields, manage irrigation, monitor soil, predict harvests, "
             "control greenhouse climate and coordinate machinery",
    )

    # -------- Value sets --------
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_bool = ValueSet("Boolean")
    vs_dt = ValueSet("DateTime")
    vs_location = ValueSet("GeoCoordinates")
    vs_crop_stage = ValueSet("CropStage", "planted, germination, vegetative, flowering, fruiting, harvest")
    vs_machine_kind = ValueSet("MachineKind", "tractor, harvester, sprayer, drone")
    vs_machine_state = ValueSet("MachineState", "idle, en_route, working, maintenance")

    # -------- Entity: Field --------
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
    field.add_attribute(
        DerivedAttribute(
            "irrigation_need", vs_float,
            "Estimated irrigation need in mm",
            "Computed from soil moisture, weather forecast and crop stage",
        )
    )
    model.add_entity(field)

    # -------- Entity: Crop --------
    crop = Entity("Crop", description="Crop being grown in a field")
    crop.add_attribute(Attribute("id", vs_string))
    crop.add_attribute(Attribute("type", vs_string, "wheat, corn, soybeans, etc."))
    crop.add_attribute(Attribute("planting_date", vs_dt))
    crop.add_attribute(Attribute("growth_stage", vs_crop_stage))
    crop.add_attribute(
        HistoricalAttribute("height", vs_float, "Average plant height in cm over time")
    )
    crop.add_attribute(
        HistoricalAttribute("health_index", vs_float, "Crop health score 0–100 over time")
    )
    crop.add_attribute(
        HistoricalAttribute("ndvi", vs_float, "Normalised Difference Vegetation Index over time")
    )
    crop.add_attribute(
        DerivedAttribute(
            "predicted_yield", vs_float,
            "Predicted yield in tons/hectare",
            "ML prediction based on growth patterns, weather, soil conditions and NDVI",
        )
    )
    crop.add_attribute(
        DerivedAttribute(
            "harvest_date", vs_dt,
            "Estimated harvest date",
            "Calculated from growth stage and weather forecast",
        )
    )
    model.add_entity(crop)

    # -------- Entity: IrrigationSystem --------
    irrigation = Entity("IrrigationSystem", description="Automated irrigation system")
    irrigation.add_attribute(Attribute("id", vs_string))
    irrigation.add_attribute(Attribute("type", vs_string, "drip, sprinkler, pivot"))
    irrigation.add_attribute(Attribute("active", vs_bool))
    irrigation.add_attribute(
        HistoricalAttribute("water_flow", vs_float, "Liters per minute over time")
    )
    irrigation.add_attribute(
        HistoricalAttribute("water_usage", vs_float, "Cumulative liters used over time")
    )
    model.add_entity(irrigation)

    # -------- Entity: WeatherStation --------
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
        HistoricalAttribute("solar_radiation", vs_float, "Solar radiation in W/m^2 over time")
    )
    model.add_entity(weather)

    # -------- Entity: GreenHouse --------
    greenhouse = Entity("GreenHouse", description="Climate-controlled greenhouse")
    greenhouse.add_attribute(Attribute("id", vs_string))
    greenhouse.add_attribute(Attribute("location", vs_location))
    greenhouse.add_attribute(Attribute("ventilation_open", vs_bool))
    greenhouse.add_attribute(Attribute("heater_on", vs_bool))
    greenhouse.add_attribute(
        HistoricalAttribute("inside_temperature", vs_float, "Inside temperature over time")
    )
    greenhouse.add_attribute(
        HistoricalAttribute("inside_humidity", vs_float, "Inside humidity over time")
    )
    greenhouse.add_attribute(
        HistoricalAttribute("co2_ppm", vs_float, "CO2 concentration in ppm over time")
    )
    model.add_entity(greenhouse)

    # -------- Entity: AgriculturalMachine --------
    machine = Entity("AgriculturalMachine", description="Tractor, harvester, sprayer or drone")
    machine.add_attribute(Attribute("id", vs_string))
    machine.add_attribute(Attribute("kind", vs_machine_kind))
    machine.add_attribute(Attribute("state", vs_machine_state))
    machine.add_attribute(
        HistoricalAttribute("location", vs_location, "GPS position over time")
    )
    machine.add_attribute(
        HistoricalAttribute("fuel_level", vs_float, "Fuel/battery level percentage over time")
    )
    machine.add_attribute(
        HistoricalAttribute("hours_worked", vs_float, "Cumulative hours over time")
    )
    model.add_entity(machine)

    # -------- Relationships --------
    model.add_relationship(Relationship("planted_in", [crop, field]))
    model.add_relationship(Relationship("irrigates", [irrigation, field]))
    model.add_relationship(Relationship("monitors", [weather, field]))
    model.add_relationship(Relationship("hosts", [greenhouse, crop]))
    model.add_relationship(Relationship("operates_in", [machine, field]))

    # -------- Interfaces --------
    # IrrigationSystem: 1U
    control_irrigation = Interface(
        "control_irrigation", irrigation, InterfaceType.UPDATE,
        "Control irrigation system",
        parameters=["active", "flow_rate"],
        security_constraints=["Requires farm manager authorisation"],
    )
    model.add_interface(control_irrigation)

    # Field: 1Q + 1A
    get_field_status = Interface(
        "get_field_status", field, InterfaceType.QUERY,
        "Get comprehensive field status",
        returns="Soil conditions, moisture, nutrients, irrigation need",
        security_constraints=["Requires farm access"],
    )
    model.add_interface(get_field_status)

    plan_treatment = Interface(
        "plan_treatment", field, InterfaceType.ANALYTICAL,
        "Plan a fertilisation/treatment campaign for a field",
        parameters=["objective", "horizon_days"],
        returns="Plan of (date, treatment, dosage)",
        security_constraints=["Requires agronomist authorisation"],
    )
    model.add_interface(plan_treatment)

    # Crop: 1A
    predict_yield = Interface(
        "predict_yield", crop, InterfaceType.ANALYTICAL,
        "Predict crop yield",
        parameters=["field_id"],
        returns="Yield prediction with confidence interval",
        security_constraints=["Internal analytics system"],
    )
    model.add_interface(predict_yield)

    # WeatherStation: 1U
    push_weather = Interface(
        "push_reading", weather, InterfaceType.UPDATE,
        "Push a weather reading",
        parameters=["temperature", "humidity", "rainfall", "wind_speed", "solar_radiation",
                    "timestamp"],
        security_constraints=["Requires weather-station authentication"],
    )
    model.add_interface(push_weather)

    # GreenHouse: 1U + 1Q
    set_greenhouse_climate = Interface(
        "set_climate", greenhouse, InterfaceType.UPDATE,
        "Command greenhouse actuators (ventilation, heater)",
        parameters=["ventilation_open", "heater_on"],
        security_constraints=["Requires greenhouse manager authorisation"],
    )
    model.add_interface(set_greenhouse_climate)

    get_greenhouse_climate = Interface(
        "get_climate", greenhouse, InterfaceType.QUERY,
        "Get current and recent climate readings",
        parameters=["since (datetime)"],
        returns="Time-series of inside_temperature, inside_humidity, co2_ppm",
        security_constraints=["Requires greenhouse staff authentication"],
    )
    model.add_interface(get_greenhouse_climate)

    # AgriculturalMachine: 1R + 1U
    assign_machine_to_field = Interface(
        "assign_to_field", machine, InterfaceType.RELATIONSHIP,
        "Assign a machine to operate in a specific field",
        parameters=["field_id", "task"],
        security_constraints=["Requires fleet manager authorisation"],
    )
    model.add_interface(assign_machine_to_field)

    push_machine_telemetry = Interface(
        "push_telemetry", machine, InterfaceType.UPDATE,
        "Push machine telemetry (location, fuel, hours)",
        parameters=["location", "fuel_level", "hours_worked", "timestamp"],
        security_constraints=["Requires machine telemetry authentication"],
    )
    model.add_interface(push_machine_telemetry)

    # -------- Incoming events --------
    model.add_incoming_event(IncomingEvent(
        "sensor_data", get_field_status,
        "Soil and environmental sensor data",
        event_source="IoT soil sensors and field monitors",
    ))
    model.add_incoming_event(IncomingEvent(
        "weather_update", push_weather,
        "Fetch weather station data",
        event_source="Weather station",
    ))
    model.add_incoming_event(IncomingEvent(
        "greenhouse_telemetry", get_greenhouse_climate,
        "Inside-greenhouse climate telemetry",
        event_source="Greenhouse climate sensors",
    ))
    model.add_incoming_event(IncomingEvent(
        "machine_telemetry", push_machine_telemetry,
        "Telemetry from agricultural machinery",
        event_source="On-board machine telemetry unit",
    ))

    # -------- Outgoing events --------
    model.add_outgoing_event(OutgoingEvent(
        "irrigation_command", control_irrigation,
        "Activate irrigation based on soil moisture",
        event_target="Irrigation controller",
        trigger_condition="Soil moisture below threshold and no rain forecast",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "pest_alert", predict_yield,
        "Alert farmer of potential pest or disease issues",
        event_target="Farm management mobile app",
        trigger_condition="Crop health index drops significantly",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "climate_command", set_greenhouse_climate,
        "Open ventilation or activate heater in greenhouse",
        event_target="Greenhouse climate controller",
        trigger_condition="Inside temperature or humidity outside crop comfort band",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "harvest_dispatch", assign_machine_to_field,
        "Dispatch harvester to a field that has reached harvest stage",
        event_target="Fleet dispatch system",
        trigger_condition="Crop growth_stage transitions to harvest",
    ))

    return model
