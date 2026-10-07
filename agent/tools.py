import json
from datetime import datetime

# In-memory mock database for the clinic
MOCK_DATABASE = {
    "doctors": [
        {"id": "doc_1", "name": "Dr. Sarah Smith", "specialty": "General Practice"},
        {"id": "doc_2", "name": "Dr. James Wilson", "specialty": "Cardiology"}
    ],
    "appointments": {}
}

def check_availability(doctor_name: str, date: str) -> str:
    """Check available time slots for a specific doctor on a given date."""
    # Simple mock implementation
    slots = ["09:00 AM", "11:00 AM", "02:00 PM", "04:30 PM"]
    return json.dumps({
        "doctor": doctor_name,
        "date": date,
        "available_slots": slots
    })

def book_appointment(patient_name: str, doctor_name: str, time_slot: str, reason: str) -> str:
    """Book an appointment for a patient with a doctor at a specific time slot."""
    appt_id = f"APT-{int(datetime.now().timestamp())}"
    
    booking_record = {
        "appointment_id": appt_id,
        "patient_name": patient_name,
        "doctor_name": doctor_name,
        "time_slot": time_slot,
        "reason": reason,
        "status": "Confirmed"
    }
    
    MOCK_DATABASE["appointments"][appt_id] = booking_record
    return json.dumps(booking_record)

def cancel_appointment(appointment_id: str) -> str:
    """Cancel an existing appointment by its ID."""
    if appointment_id in MOCK_DATABASE["appointments"]:
        MOCK_DATABASE["appointments"][appointment_id]["status"] = "Cancelled"
        return json.dumps({"status": "Success", "message": f"Appointment {appointment_id} has been cancelled."})
    return json.dumps({"status": "Error", "message": "Appointment ID not found."})