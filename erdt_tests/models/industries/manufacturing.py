"""
Manufacturing Digital Twin Model.

This model represents a manufacturing production line with machines, sensors,
and products for process optimization and predictive maintenance.

Goal: Monitor production processes, predict machine failures, optimize production
efficiency, and ensure quality control.
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


def create_manufacturing_model() -> ERDTModel:
    """
    Create a manufacturing digital twin model.
    
    Returns:
        ERDTModel: Complete manufacturing model
    """
    model = ERDTModel(
        name="Manufacturing Digital Twin",
        description="Digital twin for smart manufacturing and production optimization",
        goal="Monitor production, predict failures, and optimize efficiency"
    )
    
    # Value sets
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_status = ValueSet("MachineStatus", "running, idle, maintenance, error")
    vs_datetime = ValueSet("DateTime")
    
    # Entity: ProductionLine
    production_line = Entity("ProductionLine", description="Manufacturing production line")
    production_line.add_attribute(Attribute("id", vs_string))
    production_line.add_attribute(Attribute("name", vs_string))
    production_line.add_attribute(
        HistoricalAttribute("production_count", vs_int, "Total units produced over time")
    )
    production_line.add_attribute(
        DerivedAttribute("efficiency", vs_float, "Production efficiency percentage",
                        "Calculated from production count vs. target")
    )
    model.add_entity(production_line)
    
    # Entity: Machine
    machine = Entity("Machine", description="Manufacturing machine or equipment")
    machine.add_attribute(Attribute("id", vs_string))
    machine.add_attribute(Attribute("name", vs_string))
    machine.add_attribute(Attribute("status", vs_status))
    machine.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Operating temperature in Celsius")
    )
    machine.add_attribute(
        HistoricalAttribute("vibration", vs_float, "Vibration level")
    )
    machine.add_attribute(
        DerivedAttribute("failure_probability", vs_float, "Predicted failure probability",
                        "ML model prediction based on sensor data")
    )
    model.add_entity(machine)
    
    # Entity: Sensor
    sensor = Entity("Sensor", description="IoT sensor monitoring equipment")
    sensor.add_attribute(Attribute("id", vs_string))
    sensor.add_attribute(Attribute("type", vs_string, "temperature, pressure, vibration, etc."))
    sensor.add_attribute(HistoricalAttribute("value", vs_float, "Sensor readings over time"))
    model.add_entity(sensor)
    
    # Entity: Product
    product = Entity("Product", description="Manufactured product")
    product.add_attribute(Attribute("id", vs_string))
    product.add_attribute(Attribute("name", vs_string))
    product.add_attribute(Attribute("quality_score", vs_float))
    product.add_attribute(Attribute("production_timestamp", vs_datetime))
    model.add_entity(product)
    
    # Relationships
    model.add_relationship(Relationship("contains", [production_line, machine]))
    model.add_relationship(Relationship("monitors", [sensor, machine]))
    model.add_relationship(Relationship("produces", [machine, product]))
    
    # Interfaces
    set_machine_status = Interface(
        "set_machine_status", machine, InterfaceType.UPDATE,
        "Update machine operational status",
        parameters=["status"],
        security_constraints=["Requires operator authentication"]
    )
    model.add_interface(set_machine_status)
    
    get_metrics = Interface(
        "get_metrics", machine, InterfaceType.QUERY,
        "Get machine performance metrics",
        returns="Metrics object with temperature, vibration, efficiency",
        security_constraints=["Requires monitoring system access"]
    )
    model.add_interface(get_metrics)
    
    schedule_maintenance = Interface(
        "schedule_maintenance", machine, InterfaceType.ANALYTICAL,
        "Schedule predictive maintenance based on ML predictions",
        parameters=["maintenance_type", "scheduled_time"],
        security_constraints=["Requires maintenance manager authorization"]
    )
    model.add_interface(schedule_maintenance)
    
    # Data flows
    model.add_incoming_event(IncomingEvent(
        "sensor_telemetry", set_machine_status,
        "Real-time sensor data from IoT devices",
        event_source="IoT sensor network",
    ))
    
    model.add_incoming_event(IncomingEvent(
        "machine_status_poll", get_metrics,
        "Periodic polling of machine metrics",
        event_source="Machine control system",
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "maintenance_alert", schedule_maintenance,
        "Alert when predictive maintenance is needed",
        event_target="Maintenance management system",
        trigger_condition="Failure probability exceeds threshold"
    ))
    
    return model
