"""
Healthcare Digital Twin Model.

This model represents a hospital ward or remote-monitoring deployment, including
patients, medical devices, vital-sign streams, treatments, medications, beds and
healthcare workers. The DT supports continuous patient monitoring, personalised
treatment and emergency alerting, with strict privacy and access-control concerns.

Goal: Monitor patient vital signs, provide real-time health status, enable
personalised treatment, manage medication administration, coordinate caregiver
assignments and trigger emergency alerts.
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
        description="Digital twin for patient monitoring and personalised healthcare",
        goal="Monitor vital signs, enable personalised treatment, manage medication, "
             "coordinate caregivers and trigger emergency response",
    )

    # -------- Value sets --------
    vs_string = ValueSet("String")
    vs_float = ValueSet("Float")
    vs_int = ValueSet("Integer")
    vs_bool = ValueSet("Boolean")
    vs_dt = ValueSet("DateTime")
    vs_status = ValueSet("HealthStatus", "normal, warning, critical")
    vs_role = ValueSet("CaregiverRole", "doctor, nurse, technician")

    # -------- Entity: Patient --------
    patient = Entity("Patient", description="Patient being monitored")
    patient.add_attribute(Attribute("id", vs_string))
    patient.add_attribute(Attribute("name", vs_string))
    patient.add_attribute(Attribute("age", vs_int))
    patient.add_attribute(Attribute("admission_date", vs_dt))
    patient.add_attribute(Attribute("primary_diagnosis", vs_string))
    patient.add_attribute(
        DerivedAttribute(
            "health_status", vs_status,
            "Overall health assessment",
            "Computed from vital signs trends, treatments and medical history",
        )
    )
    patient.add_attribute(
        DerivedAttribute(
            "early_warning_score", vs_int,
            "NEWS2-style early-warning composite score",
            "Computed from current vitals (HR, BP, RR, SpO2, temp, consciousness)",
        )
    )
    model.add_entity(patient)

    # -------- Entity: MedicalDevice --------
    device = Entity("MedicalDevice", description="Medical monitoring or therapy device")
    device.add_attribute(Attribute("id", vs_string))
    device.add_attribute(Attribute("type", vs_string, "ECG, BP cuff, pulse-ox, infusion pump, etc."))
    device.add_attribute(Attribute("manufacturer", vs_string))
    device.add_attribute(Attribute("location", vs_string))
    device.add_attribute(Attribute("calibrated_until", vs_dt))
    model.add_entity(device)

    # -------- Entity: VitalSigns --------
    vitals = Entity("VitalSigns", description="Patient vital signs measurements (time-series streams)")
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
    vitals.add_attribute(
        HistoricalAttribute("respiratory_rate", vs_int, "Breaths per minute over time")
    )
    vitals.add_attribute(
        HistoricalAttribute("glucose_level", vs_float, "Blood glucose mg/dL over time")
    )
    model.add_entity(vitals)

    # -------- Entity: Treatment --------
    treatment = Entity("Treatment", description="Medical treatment or intervention")
    treatment.add_attribute(Attribute("id", vs_string))
    treatment.add_attribute(Attribute("type", vs_string))
    treatment.add_attribute(Attribute("start_time", vs_dt))
    treatment.add_attribute(Attribute("end_time", vs_dt))
    treatment.add_attribute(Attribute("notes", vs_string))
    model.add_entity(treatment)

    # -------- Entity: Medication --------
    medication = Entity("Medication", description="Medication administration record")
    medication.add_attribute(Attribute("id", vs_string))
    medication.add_attribute(Attribute("drug_name", vs_string))
    medication.add_attribute(Attribute("dose_mg", vs_float))
    medication.add_attribute(Attribute("scheduled_time", vs_dt))
    medication.add_attribute(Attribute("administered_time", vs_dt))
    medication.add_attribute(
        HistoricalAttribute("infusion_rate", vs_float, "ml/h over time, when applicable")
    )
    model.add_entity(medication)

    # -------- Entity: Bed --------
    bed = Entity("Bed", description="Hospital bed (with optional smart features)")
    bed.add_attribute(Attribute("id", vs_string))
    bed.add_attribute(Attribute("ward", vs_string))
    bed.add_attribute(Attribute("occupied", vs_bool))
    bed.add_attribute(
        HistoricalAttribute("position_state", vs_string, "Bed angle / posture state over time")
    )
    model.add_entity(bed)

    # -------- Entity: Caregiver --------
    caregiver = Entity("Caregiver", description="Healthcare worker assigned to patients")
    caregiver.add_attribute(Attribute("id", vs_string))
    caregiver.add_attribute(Attribute("name", vs_string))
    caregiver.add_attribute(Attribute("role", vs_role))
    caregiver.add_attribute(Attribute("on_shift", vs_bool))
    model.add_entity(caregiver)

    # -------- Relationships --------
    model.add_relationship(Relationship("has_vitals", [patient, vitals]))
    model.add_relationship(Relationship("monitored_by", [patient, device]))
    model.add_relationship(Relationship("receives", [patient, treatment]))
    model.add_relationship(Relationship("takes", [patient, medication]))
    model.add_relationship(Relationship("occupies", [patient, bed]))
    model.add_relationship(Relationship("cares_for", [caregiver, patient]))

    # -------- Interfaces --------
    # VitalSigns: 1U
    update_vitals = Interface(
        "update_vitals", vitals, InterfaceType.UPDATE,
        "Update patient vital signs",
        parameters=["heart_rate", "blood_pressure", "temperature", "oxygen_saturation",
                    "respiratory_rate", "glucose_level"],
        security_constraints=["Requires medical device authentication", "HIPAA/GDPR compliant"],
    )
    model.add_interface(update_vitals)

    # Patient: 1Q + 1A
    get_patient_history = Interface(
        "get_patient_history", patient, InterfaceType.QUERY,
        "Retrieve patient medical history and vital signs",
        parameters=["time_range"],
        returns="Historical vital signs, treatments and medications",
        security_constraints=[
            "Requires healthcare provider authentication",
            "Patient must be assigned to caller",
            "HIPAA/GDPR compliant audit log",
        ],
    )
    model.add_interface(get_patient_history)

    alert_medical_staff = Interface(
        "alert_medical_staff", patient, InterfaceType.ANALYTICAL,
        "Alert medical staff of critical condition",
        parameters=["alert_type", "severity"],
        security_constraints=["Automated system with audit logging"],
    )
    model.add_interface(alert_medical_staff)

    # Treatment: 1U + 1Q
    record_treatment = Interface(
        "record_treatment", treatment, InterfaceType.UPDATE,
        "Open or close a treatment record",
        parameters=["patient_id", "type", "start_time", "end_time"],
        security_constraints=["Requires attending doctor authentication", "HIPAA/GDPR compliant"],
    )
    model.add_interface(record_treatment)

    list_active_treatments = Interface(
        "list_active_treatments", treatment, InterfaceType.QUERY,
        "List all currently open treatments for a patient",
        parameters=["patient_id"],
        returns="List of treatment records",
        security_constraints=["Requires assigned-caregiver authentication"],
    )
    model.add_interface(list_active_treatments)

    # Medication: 1U
    administer_medication = Interface(
        "administer", medication, InterfaceType.UPDATE,
        "Mark a scheduled medication as administered",
        parameters=["medication_id", "administered_time", "actual_dose"],
        security_constraints=[
            "Requires nurse/doctor authentication",
            "Six-rights of medication administration check",
            "Audit logged",
        ],
    )
    model.add_interface(administer_medication)

    # Bed: 1R
    assign_bed = Interface(
        "assign_bed", bed, InterfaceType.RELATIONSHIP,
        "Assign a patient to this bed",
        parameters=["patient_id"],
        security_constraints=["Requires admissions desk authentication"],
    )
    model.add_interface(assign_bed)

    # Caregiver: 1R + 1Q
    assign_caregiver = Interface(
        "assign_to_patient", caregiver, InterfaceType.RELATIONSHIP,
        "Assign a caregiver to a patient for the current shift",
        parameters=["patient_id", "shift_start", "shift_end"],
        security_constraints=["Requires charge-nurse authorization"],
    )
    model.add_interface(assign_caregiver)

    list_assigned_patients = Interface(
        "list_assigned_patients", caregiver, InterfaceType.QUERY,
        "List the patients assigned to this caregiver on the current shift",
        returns="List of patient ids and bed locations",
        security_constraints=["Requires caregiver authentication"],
    )
    model.add_interface(list_assigned_patients)

    # -------- Incoming events --------
    model.add_incoming_event(IncomingEvent(
        "continuous_monitoring", update_vitals,
        "Continuous vital signs from medical devices",
        event_source="Patient monitoring devices",
    ))
    model.add_incoming_event(IncomingEvent(
        "vitals_check", update_vitals,
        "Periodic manual vital signs measurement",
        event_source="Bedside nurse station",
    ))
    model.add_incoming_event(IncomingEvent(
        "med_dispense", administer_medication,
        "Medication dispensed by smart cabinet",
        event_source="Smart medication dispenser",
    ))
    model.add_incoming_event(IncomingEvent(
        "shift_assignment", assign_caregiver,
        "Shift planner assigns caregiver to patients",
        event_source="HR shift planner",
    ))

    # -------- Outgoing events --------
    model.add_outgoing_event(OutgoingEvent(
        "emergency_alert", alert_medical_staff,
        "Critical condition detected, immediate attention required",
        event_target="Medical staff notification system",
        trigger_condition="Vital signs outside safe thresholds OR EWS >= 7",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "med_due_alert", administer_medication,
        "Notify nurse station that a scheduled medication is due",
        event_target="Nurse station dashboard",
        trigger_condition="scheduled_time reached AND administered_time still empty",
    ))
    model.add_outgoing_event(OutgoingEvent(
        "fall_risk_alert", update_vitals,
        "Notify caregiver of elevated fall risk",
        event_target="Caregiver mobile device",
        trigger_condition="Bed position changes outside policy AND patient flagged at-risk",
    ))

    return model
