"""
Logistics Digital Twin Model - Based on the case study from the ERDT paper.

This model represents the Mercadona Tech logistics chain for online grocery delivery,
including warehouses (hives), workers (pickers), delivery trucks, and drivers.

Goal: Locate all workers in the geographical environment and within warehouses to apply
risk control measures, alert when trucks enter low-emission zones (LEZ), and analyze
routes traveled during the day.
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


def create_logistics_model() -> ERDTModel:
    """
    Create the logistics digital twin model from the ERDT paper case study.
    
    Returns:
        ERDTModel: Complete logistics model with entities, relationships, interfaces, and data flows
    """
    # Create the model
    model = ERDTModel(
        name="Logistics Digital Twin",
        description="Digital twin for online grocery delivery logistics chain",
        goal="Locate workers, alert on LEZ violations, and analyze daily routes"
    )
    
    # Define value sets
    vs_string = ValueSet("String", "Text values")
    vs_location = ValueSet("GeoCoordinates", "GPS coordinates (latitude, longitude)")
    vs_indoor_location = ValueSet("IndoorLocation", "Indoor positioning coordinates")
    vs_blueprint = ValueSet("Blueprint", "Visual representation of warehouse layout")
    
    # Entity: Hive (warehouse)
    hive = Entity(
        name="Hive",
        description="Warehouse facility where orders are prepared"
    )
    hive.add_attribute(Attribute("name", vs_string, "Name of the warehouse"))
    hive.add_attribute(Attribute("blueprint", vs_blueprint, "Visual layout of the warehouse"))
    model.add_entity(hive)
    
    # Entity: Picker (warehouse worker)
    picker = Entity(
        name="Picker",
        description="Worker who prepares orders in the warehouse"
    )
    picker.add_attribute(Attribute("id", vs_string, "Unique identifier"))
    picker.add_attribute(Attribute("name", vs_string, "Worker name"))
    picker.add_attribute(
        HistoricalAttribute("indoor_location", vs_indoor_location, "Position within warehouse over time")
    )
    model.add_entity(picker)
    
    # Entity: Truck
    truck = Entity(
        name="Truck",
        description="Vehicle that delivers orders"
    )
    truck.add_attribute(Attribute("license_plate", vs_string, "Vehicle registration"))
    truck.add_attribute(
        HistoricalAttribute("location", vs_location, "GPS coordinates over time")
    )
    model.add_entity(truck)
    
    # Entity: Driver
    driver = Entity(
        name="Driver",
        description="Person who drives the truck and delivers orders"
    )
    driver.add_attribute(Attribute("driver_license", vs_string, "Driver's license number"))
    driver.add_attribute(Attribute("name", vs_string, "Driver name"))
    driver.add_attribute(
        DerivedAttribute(
            "location",
            vs_location,
            "Current location derived from driven truck",
            "Location of the truck currently driven by this driver"
        )
    )
    model.add_entity(driver)
    
    # Relationships
    works_in = Relationship(
        name="works_in",
        entities=[picker, hive],
        description="Picker works in a specific hive"
    )
    model.add_relationship(works_in)
    
    delivers_from = Relationship(
        name="delivers_from",
        entities=[truck, hive],
        description="Truck delivers orders from a specific hive"
    )
    model.add_relationship(delivers_from)
    
    driven_by = Relationship(
        name="driven_by",
        entities=[truck, driver],
        description="Truck is driven by a specific driver"
    )
    model.add_relationship(driven_by)
    
    # Interfaces for Picker
    set_location_picker = Interface(
        name="set_location",
        entity=picker,
        interface_type=InterfaceType.UPDATE,
        description="Updates the indoor location of the picker",
        parameters=["indoor_location"],
        security_constraints=["Requires telemetry system authentication"]
    )
    model.add_interface(set_location_picker)
    
    get_location_picker = Interface(
        name="get_location",
        entity=picker,
        interface_type=InterfaceType.QUERY,
        description="Returns current or historical indoor location",
        parameters=["datetime (optional)"],
        returns="IndoorLocation",
        security_constraints=["Requires operations team authorization"]
    )
    model.add_interface(get_location_picker)
    
    # Interfaces for Truck
    set_location_truck = Interface(
        name="set_location",
        entity=truck,
        interface_type=InterfaceType.UPDATE,
        description="Updates the GPS location of the truck",
        parameters=["location"],
        security_constraints=["Requires GPS system authentication"]
    )
    model.add_interface(set_location_truck)
    
    assign_driver_truck = Interface(
        name="assign_driver",
        entity=truck,
        interface_type=InterfaceType.RELATIONSHIP,
        description="Assigns a driver to this truck",
        parameters=["driver"],
        security_constraints=["Requires fleet management authorization"]
    )
    model.add_interface(assign_driver_truck)
    
    # Interfaces for Driver
    get_location_driver = Interface(
        name="get_location",
        entity=driver,
        interface_type=InterfaceType.QUERY,
        description="Returns location of truck driven by this driver",
        parameters=["datetime (optional)"],
        returns="GeoCoordinates or empty if not driving",
        security_constraints=["Requires operations team authorization"]
    )
    model.add_interface(get_location_driver)
    
    # Interfaces for Hive
    get_blueprints = Interface(
        name="get_blueprints",
        entity=hive,
        interface_type=InterfaceType.QUERY,
        description="Returns visual representation of warehouse layout",
        returns="Blueprint",
        security_constraints=["Requires operations team authorization"]
    )
    model.add_interface(get_blueprints)
    
    # Data Flows: Incoming Events
    picker_telemetry = IncomingEvent(
        name="picker_telemetry",
        target_interface=set_location_picker,
        description="Updates picker's indoor location from telemetry system",
        event_source="Indoor positioning system worn by picker",
    )
    model.add_incoming_event(picker_telemetry)
    
    driver_assigned = IncomingEvent(
        name="driver_assigned",
        target_interface=assign_driver_truck,
        description="Assigns driver to truck when shift starts",
        event_source="Fleet management system",
    )
    model.add_incoming_event(driver_assigned)
    
    # Periodic GPS polling as incoming event
    truck_gps = IncomingEvent(
        name="truck_gps_coordinates",
        target_interface=set_location_truck,
        description="Periodically fetches truck GPS coordinates",
        event_source="Truck GPS device",
    )
    model.add_incoming_event(truck_gps)
    
    # Data Flows: Outgoing Events
    lez_alert = OutgoingEvent(
        name="truck_entered_lez",
        source_interface=set_location_truck,
        description="Alerts operations team when truck enters restricted low-emission zone",
        event_target="Operations management dashboard",
        trigger_condition="Truck location enters predefined LEZ boundary"
    )
    model.add_outgoing_event(lez_alert)
    
    return model
