"""
Manufacturing Digital Twin Model.

This model represents a smart manufacturing plant including production lines,
machines, sensors, operators, products, quality inspections and maintenance
records. The DT supports OEE monitoring, predictive maintenance and process
optimisation.

Goal: Monitor production processes, predict machine failures, optimise
production efficiency, ensure quality control and coordinate operator
assignments.
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
        goal="Monitor production, predict failures, optimise efficiency, ensure quality "
             "and coordinate operator assignments",
    )

    # -------- Value sets --------
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_bool = ValueSet("Boolean")
    vs_status = ValueSet("MachineStatus", "running, idle, maintenance, error")
    vs_dt = ValueSet("DateTime")
    vs_qa = ValueSet("QualityVerdict", "pass, rework, scrap")

    # -------- Entity: ProductionLine --------
    production_line = Entity("ProductionLine", description="Manufacturing production line")
    production_line.add_attribute(Attribute("id", vs_string))
    production_line.add_attribute(Attribute("name", vs_string))
    production_line.add_attribute(Attribute("target_throughput", vs_int, "Units per hour target"))
    production_line.add_attribute(
        HistoricalAttribute("production_count", vs_int, "Total units produced over time")
    )
    production_line.add_attribute(
        DerivedAttribute(
            "efficiency", vs_float,
            "Production efficiency percentage (OEE-style)",
            "Calculated from availability * performance * quality",
        )
    )
    production_line.add_attribute(
        DerivedAttribute(
            "bottleneck_machine_id", vs_string,
            "Identifier of the slowest machine in the line",
            "Computed from comparative cycle times of contained machines",
        )
    )
    model.add_entity(production_line)

    # -------- Entity: Machine --------
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
        HistoricalAttribute("cycle_time", vs_float, "Time per produced unit (seconds)")
    )
    machine.add_attribute(
        DerivedAttribute(
            "failure_probability", vs_float,
            "Predicted failure probability (0–1)",
            "ML model prediction based on sensor data and maintenance history",
        )
    )
    machine.add_attribute(
        DerivedAttribute(
            "oee", vs_float,
            "Overall Equipment Effectiveness for this machine",
            "Computed from availability, performance and first-pass quality",
        )
    )
    model.add_entity(machine)

    # -------- Entity: Sensor --------
    sensor = Entity("Sensor", description="IoT sensor monitoring equipment")
    sensor.add_attribute(Attribute("id", vs_string))
    sensor.add_attribute(Attribute("type", vs_string, "temperature, pressure, vibration, etc."))
    sensor.add_attribute(Attribute("unit", vs_string, "Measurement unit"))
    sensor.add_attribute(HistoricalAttribute("value", vs_float, "Sensor readings over time"))
    model.add_entity(sensor)

    # -------- Entity: Product --------
    product = Entity("Product", description="Manufactured product")
    product.add_attribute(Attribute("id", vs_string))
    product.add_attribute(Attribute("name", vs_string))
    product.add_attribute(Attribute("quality_score", vs_float))
    product.add_attribute(Attribute("production_timestamp", vs_dt))
    model.add_entity(product)

    # -------- Entity: QualityInspection --------
    qa = Entity("QualityInspection", description="Quality inspection event of a product")
    qa.add_attribute(Attribute("id", vs_string))
    qa.add_attribute(Attribute("verdict", vs_qa))
    qa.add_attribute(Attribute("inspection_timestamp", vs_dt))
    qa.add_attribute(Attribute("defect_code", vs_string, "Empty when verdict=pass"))
    qa.add_attribute(Attribute("inspector_id", vs_string))
    model.add_entity(qa)

    # -------- Entity: MaintenanceLog --------
    maintenance = Entity("MaintenanceLog", description="Maintenance record for a machine")
    maintenance.add_attribute(Attribute("id", vs_string))
    maintenance.add_attribute(Attribute("kind", vs_string, "preventive / corrective / predictive"))
    maintenance.add_attribute(Attribute("opened_at", vs_dt))
    maintenance.add_attribute(Attribute("closed_at", vs_dt))
    maintenance.add_attribute(Attribute("notes", vs_string))
    model.add_entity(maintenance)

    # -------- Entity: Operator --------
    operator = Entity("Operator", description="Shop-floor operator")
    operator.add_attribute(Attribute("id", vs_string))
    operator.add_attribute(Attribute("name", vs_string))
    operator.add_attribute(Attribute("certified_machines", vs_string, "Comma-separated machine ids"))
    operator.add_attribute(
        HistoricalAttribute("active_machine_id", vs_string, "Machine currently operated")
    )
    model.add_entity(operator)

    # -------- Relationships --------
    model.add_relationship(Relationship("contains", [production_line, machine]))
    model.add_relationship(Relationship("monitors", [sensor, machine]))
    model.add_relationship(Relationship("produces", [machine, product]))
    model.add_relationship(Relationship("inspects", [qa, product]))
    model.add_relationship(Relationship("performed_on", [maintenance, machine]))
    model.add_relationship(Relationship("operates", [operator, machine]))

    # -------- Interfaces --------
    # Machine: 1U + 1Q + 1A
    set_machine_status = Interface(
        "set_machine_status", machine, InterfaceType.UPDATE,
        "Update machine operational status",
        parameters=["status"],
        security_constraints=["Requires operator authentication"],
    )
    model.add_interface(set_machine_status)

    get_metrics = Interface(
        "get_metrics", machine, InterfaceType.QUERY,
        "Get machine performance metrics",
        returns="Metrics object with temperature, vibration, cycle_time, OEE",
        security_constraints=["Requires monitoring system access"],
    )
    model.add_interface(get_metrics)

    schedule_maintenance = Interface(
        "schedule_maintenance", machine, InterfaceType.ANALYTICAL,
        "Schedule predictive maintenance based on ML predictions",
        parameters=["maintenance_type", "scheduled_time"],
        security_constraints=["Requires maintenance manager authorization"],
    )
    model.add_interface(schedule_maintenance)

    # ProductionLine: 1Q + 1A
    get_line_oee = Interface(
        "get_line_oee", production_line, InterfaceType.QUERY,
        "Get OEE metrics for the production line over a period",
        parameters=["period_start", "period_end"],
        returns="Aggregate OEE and breakdown",
        security_constraints=["Requires plant-manager authorization"],
    )
    model.add_interface(get_line_oee)

    rebalance_line = Interface(
        "rebalance_line", production_line, InterfaceType.ANALYTICAL,
        "Suggest cycle-time rebalancing across machines to relieve the bottleneck",
        parameters=["target_throughput"],
        returns="Map of machine_id -> recommended cycle_time",
        security_constraints=["Requires plant-manager authorization"],
    )
    model.add_interface(rebalance_line)

    # Sensor: 1U
    push_sensor_reading = Interface(
        "push_reading", sensor, InterfaceType.UPDATE,
        "Push a new sensor reading",
        parameters=["value", "timestamp"],
        security_constraints=["Requires sensor authentication"],
    )
    model.add_interface(push_sensor_reading)

    # QualityInspection: 1U + 1Q
    record_inspection = Interface(
        "record_inspection", qa, InterfaceType.UPDATE,
        "Record a quality inspection result for a product",
        parameters=["product_id", "verdict", "defect_code"],
        security_constraints=["Requires QA inspector authentication"],
    )
    model.add_interface(record_inspection)

    get_defect_rate = Interface(
        "get_defect_rate", qa, InterfaceType.QUERY,
        "Get rolling defect rate for a line/period",
        parameters=["line_id", "period_start", "period_end"],
        returns="Defect rate (0–1)",
        security_constraints=["Requires QA team authorization"],
    )
    model.add_interface(get_defect_rate)

    # MaintenanceLog: 1U
    open_maintenance = Interface(
        "open_log", maintenance, InterfaceType.UPDATE,
        "Open a maintenance record for a machine",
        parameters=["machine_id", "kind", "notes"],
        security_constraints=["Requires maintenance technician authentication"],
    )
    model.add_interface(open_maintenance)

    # Operator: 1R
    assign_operator = Interface(
        "assign_to_machine", operator, InterfaceType.RELATIONSHIP,
        "Assign an operator to operate a machine on shift",
        parameters=["machine_id"],
        security_constraints=["Requires shop-floor supervisor authorization"],
    )
    model.add_interface(assign_operator)

    # -------- Incoming events --------
    model.add_incoming_event(IncomingEvent(
        "sensor_telemetry", push_sensor_reading,
        "Real-time sensor data from IoT devices",
        event_source="IoT sensor network",
    ))
    model.add_incoming_event(IncomingEvent(
        "machine_status_poll", get_metrics,
        "Periodic polling of machine metrics",
        event_source="Machine control system",
    ))
    model.add_incoming_event(IncomingEvent(
        "machine_status_change", set_machine_status,
        "Machine controller signals a status change",
        event_source="PLC machine controller",
    ))
    model.add_incoming_event(IncomingEvent(
        "qa_result", record_inspection,
        "Quality inspection result is recorded",
        event_source="QA station scanner",
    ))
    model.add_incoming_event(IncomingEvent(
        "shift_assignment", assign_operator,
        "Shift planner pushes operator-machine assignments",
        event_source="MES shift planner",
    ))

    # -------- Outgoing events --------
    model.add_outgoing_event(OutgoingEvent(
        "maintenance_alert", schedule_maintenance,
        "Alert when predictive maintenance is needed",
        event_target="Maintenance management system",
        trigger_condition="Failure probability exceeds threshold",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "machine_stop", set_machine_status,
        "Issue an emergency stop to a machine",
        event_target="PLC machine controller",
        trigger_condition="Vibration sustained > critical threshold",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "rebalance_recommendation", rebalance_line,
        "Push cycle-time rebalancing to MES",
        event_target="MES",
        trigger_condition="Bottleneck cycle-time deviates > 15% from line target",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "scrap_alert", record_inspection,
        "Notify production planner when scrap rate spikes",
        event_target="Production planner dashboard",
        trigger_condition="Defect rate over last 30 minutes exceeds threshold",
    ))

    return model
