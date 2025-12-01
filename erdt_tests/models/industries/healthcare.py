"""
Healthcare Digital Twin Model.

This model represents patient monitoring with medical devices and vital signs
for personalized treatment and emergency response.

Goal: Monitor patient vital signs, provide real-time health status, enable
personalized treatment, and trigger emergency alerts.
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


def create_healthcare_model() -> ERDTModel:
    """
    Create a healthcare digital twin model.
    
    Returns:
        ERDTModel: Complete healthcare model
    """
    model = ERDTModel(
        name="Healthcare Digital Twin",
        description="Digital twin for patient monitoring and personalized healthcare",
        goal="Monitor vital signs, enable personalized treatment, and emergency response"
    )
    
    # Value sets
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_datetime = ValueSet("DateTime")
    vs_health_status = ValueSet("HealthStatus", "normal, warning, critical")
    
    # Entity: Patient
    patient = Entity("Patient", description="Patient being monitored")
    patient.add_attribute(Attribute("id", vs_string))
    patient.add_attribute(Attribute("name", vs_string))
    patient.add_attribute(Attribute("age", vs_int))
    patient.add_attribute(
        DerivedAttribute("health_status", vs_health_status, "Overall health assessment",
                        "Computed from vital signs and medical history")
    )
    model.add_entity(patient)
    
    # Entity: MedicalDevice
    device = Entity("MedicalDevice", description="Medical monitoring device")
    device.add_attribute(Attribute("id", vs_string))
    device.add_attribute(Attribute("type", vs_string, "heart monitor, blood pressure cuff, etc."))
    device.add_attribute(Attribute("location", vs_string))
    model.add_entity(device)
    
    # Entity: VitalSigns
    vitals = Entity("VitalSigns", description="Patient vital signs measurements")
    vitals.add_attribute(
        HistoricalAttribute("heart_rate", vs_int, "Heart rate in BPM over time")
    )
    vitals.add_attribute(
        HistoricalAttribute("blood_pressure_systolic", vs_int, "Systolic BP over time")
    )
    vitals.add_attribute(
        HistoricalAttribute("blood_pressure_diastolic", vs_int, "Diastolic BP over time")
    )
    vitals.add_attribute(
        HistoricalAttribute("temperature", vs_float, "Body temperature in Celsius over time")
    )
    vitals.add_attribute(
        HistoricalAttribute("oxygen_saturation", vs_float, "SpO2 percentage over time")
    )
    model.add_entity(vitals)
    
    # Entity: Treatment
    treatment = Entity("Treatment", description="Medical treatment or intervention")
    treatment.add_attribute(Attribute("id", vs_string))
    treatment.add_attribute(Attribute("type", vs_string))
    treatment.add_attribute(Attribute("start_time", vs_datetime))
    treatment.add_attribute(Attribute("end_time", vs_datetime))
    model.add_entity(treatment)
    
    # Relationships
    model.add_relationship(Relationship("has_vitals", [patient, vitals]))
    model.add_relationship(Relationship("monitored_by", [patient, device]))
    model.add_relationship(Relationship("receives", [patient, treatment]))
    
    # Interfaces
    update_vitals = Interface(
        "update_vitals", vitals, InterfaceType.UPDATE,
        "Update patient vital signs",
        parameters=["heart_rate", "blood_pressure", "temperature", "oxygen_saturation"],
        security_constraints=["Requires medical device authentication", "HIPAA compliant"]
    )
    model.add_interface(update_vitals)
    
    get_patient_history = Interface(
        "get_patient_history", patient, InterfaceType.QUERY,
        "Retrieve patient medical history and vital signs",
        parameters=["time_range"],
        returns="Historical vital signs and treatments",
        security_constraints=["Requires healthcare provider authentication", "HIPAA compliant"]
    )
    model.add_interface(get_patient_history)
    
    alert_medical_staff = Interface(
        "alert_medical_staff", patient, InterfaceType.ANALYTICAL,
        "Alert medical staff of critical condition",
        parameters=["alert_type", "severity"],
        security_constraints=["Automated system with audit logging"]
    )
    model.add_interface(alert_medical_staff)
    
    # Data flows
    model.add_incoming_event(IncomingEvent(
        "continuous_monitoring", update_vitals,
        "Continuous vital signs from medical devices",
        event_source="Patient monitoring devices",
    ))
    
    model.add_incoming_event(IncomingEvent(
        "vitals_check", update_vitals,
        "Periodic vital signs measurement",
        event_source="Medical devices",
    ))
    
    model.add_outgoing_event(OutgoingEvent(
        "emergency_alert", alert_medical_staff,
        "Critical condition detected, immediate attention required",
        event_target="Medical staff notification system",
        trigger_condition="Vital signs outside safe thresholds"
    ))
    
    return model
