import json
from datetime import datetime, timedelta, date
from clinic_connect.database import db
from clinic_connect.models import Clinic, Patient, Doctor, Appointment, Prescription, Inventory, Invoice, AuditLog, SyncLog

def seed_demo_clinic():
    """Seeds a complete mock clinic with structured data for demonstrations"""
    # 1. Check if demo clinic already exists
    demo_license = 'demo-123'
    existing_clinic = Clinic.query.filter_by(license_code=demo_license).first()
    if existing_clinic:
        return existing_clinic

    # 2. Create the demo Clinic
    clinic = Clinic(
        name='Apex Care Center',
        license_code=demo_license,
        address='102, Station Road, Civil Lines, Kanpur, UP',
        contact_number='+91 99999 88888',
        email='contact@apexcare.org'
    )
    clinic.set_password('admin')
    db.session.add(clinic)
    db.session.commit()
    
    # 3. Seed Doctors
    doctors_data = [
        ('Dr. Rajesh Kumar', 'Cardiologist', '09:00', '17:00'),
        ('Dr. Priya Sharma', 'Pediatrician', '10:00', '18:00'),
        ('Dr. Amit Patel', 'Orthopedist', '09:00', '17:00'),
        ('Dr. Sneha Reddy', 'Dermatologist', '11:00', '19:00'),
        ('Dr. Vikram Mehta', 'Neurologist', '09:00', '15:00'),
        ('Dr. Anjali Desai', 'Gynecologist', '10:00', '17:00')
    ]
    doctors = []
    for name, spec, start, end in doctors_data:
        doc = Doctor(
            clinic_id=clinic.clinic_id,
            name=name,
            specialization=spec,
            working_hours_start=start,
            working_hours_end=end,
            availability_status='Available'
        )
        db.session.add(doc)
        doctors.append(doc)
    db.session.commit()

    # 4. Seed Patients
    patients_data = [
        ('Rajesh Verma', 45, 'Male', '+91 98765 43210', 'Hypertension & chronic chest discomfort'),
        ('Meena Devi', 32, 'Female', '+91 91234 56789', 'First trimester pregnancy routine review'),
        ('Amit Kumar', 8, 'Male', '+91 99887 76655', 'High fever, dry cough, body aches'),
        ('Priya Singh', 27, 'Female', '+91 98989 89898', 'Severe allergic skin rash on arms'),
        ('Sunder Lal', 64, 'Male', '+91 97979 79797', 'Osteoarthritis left knee joint pain'),
        ('Geeta Sharma', 51, 'Female', '+91 96969 96969', 'Chronic migraine headaches')
    ]
    patients = []
    # Dates spanning the last week
    today_dt = date.today()
    for i, (name, age, gender, contact, issue) in enumerate(patients_data):
        reg_date = today_dt - timedelta(days=i*2 + 1)
        pat = Patient(
            clinic_id=clinic.clinic_id,
            name=name,
            age=age,
            gender=gender,
            contact_number=contact,
            health_issue=issue,
            registration_date=reg_date
        )
        db.session.add(pat)
        patients.append(pat)
    db.session.commit()

    # 5. Seed Inventory
    inventory_data = [
        ('Paracetamol 650mg (Dolo)', 150, 2.5, 15),
        ('Amoxicillin 500mg (Antibiotic)', 85, 12.0, 10),
        ('Amlodipine 5mg (BP)', 200, 4.5, 20),
        ('Cetirizine 10mg (Allergy)', 4, 1.5, 12),  # Trigger alert
        ('Ibuprofen 400mg (Painkiller)', 8, 3.5, 15), # Trigger alert
        ('Pantoprazole 40mg (Acidity)', 120, 5.0, 10)
    ]
    for name, qty, price, min_t in inventory_data:
        item = Inventory(
            clinic_id=clinic.clinic_id,
            name=name,
            stock_quantity=qty,
            unit_price=price,
            min_threshold=min_t
        )
        db.session.add(item)
    db.session.commit()

    # 6. Seed Past Appointments (Completed with Prescriptions & Invoices)
    # Appointment 1: Rajesh Verma - Dr. Rajesh Kumar (Cardiologist) - 2 days ago
    past_date_1 = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    appt1 = Appointment(
        clinic_id=clinic.clinic_id,
        patient_id=patients[0].patient_id,
        doctor_id=doctors[0].doctor_id,
        date=past_date_1,
        time_slot='10:30 AM',
        type='consultation',
        status='Completed',
        notes='Patient presented with high blood pressure and mild exertion dyspnea.'
    )
    db.session.add(appt1)
    db.session.flush() # Populate appt1.appointment_id
    
    meds1 = [
        {'name': 'Amlodipine 5mg (BP)', 'dosage': '1 tablet', 'frequency': 'Once daily (morning)', 'duration': '30 days'},
        {'name': 'Paracetamol 650mg (Dolo)', 'dosage': '1 tablet', 'frequency': 'As needed for headache', 'duration': '5 days'}
    ]
    presc1 = Prescription(
        appointment_id=appt1.appointment_id,
        symptoms='Elevated BP (150/95), mild dyspnea, occasional chest tightness',
        diagnosis='Stage-1 Hypertension',
        medicine_details=json.dumps(meds1)
    )
    db.session.add(presc1)
    
    inv1 = Invoice(
        clinic_id=clinic.clinic_id,
        patient_id=patients[0].patient_id,
        appointment_id=appt1.appointment_id,
        consultation_fee=300.0,
        medicine_fee=147.5, # 30*4.5 + 5*2.5
        total_amount=447.5,
        status='Paid'
    )
    db.session.add(inv1)

    # Appointment 2: Meena Devi - Dr. Anjali Desai (Gynecologist) - 3 days ago
    past_date_2 = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    appt2 = Appointment(
        clinic_id=clinic.clinic_id,
        patient_id=patients[1].patient_id,
        doctor_id=doctors[5].doctor_id,
        date=past_date_2,
        time_slot='11:00 AM',
        type='checkup',
        status='Completed',
        notes='First prenatal screening. Patient health is good. Vitals stable.'
    )
    db.session.add(appt2)
    db.session.flush()
    
    meds2 = [
        {'name': 'Folic Acid 5mg', 'dosage': '1 tablet', 'frequency': 'Once daily', 'duration': '30 days'},
        {'name': 'Pantoprazole 40mg (Acidity)', 'dosage': '1 tablet', 'frequency': 'Empty stomach morning', 'duration': '10 days'}
    ]
    presc2 = Prescription(
        appointment_id=appt2.appointment_id,
        symptoms='Nausea, mild morning sickness',
        diagnosis='Healthy pregnancy (10 weeks gestation)',
        medicine_details=json.dumps(meds2)
    )
    db.session.add(presc2)
    
    inv2 = Invoice(
        clinic_id=clinic.clinic_id,
        patient_id=patients[1].patient_id,
        appointment_id=appt2.appointment_id,
        consultation_fee=400.0,
        medicine_fee=50.0, # 10*5.0
        total_amount=450.0,
        status='Paid'
    )
    db.session.add(inv2)

    # 7. Seed Active Scheduled Appointments for TODAY
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # Appt 3: Rajesh Verma - Dr. Rajesh Kumar (Cardiologist) - Today 10:00 AM
    appt3 = Appointment(
        clinic_id=clinic.clinic_id,
        patient_id=patients[0].patient_id,
        doctor_id=doctors[0].doctor_id,
        date=today_str,
        time_slot='10:00 AM',
        type='consultation',
        status='Scheduled',
        notes='BP follow up check'
    )
    db.session.add(appt3)

    # Appt 4: Amit Kumar - Dr. Priya Sharma (Pediatrician) - Today 11:30 AM
    appt4 = Appointment(
        clinic_id=clinic.clinic_id,
        patient_id=patients[2].patient_id,
        doctor_id=doctors[1].doctor_id,
        date=today_str,
        time_slot='11:30 AM',
        type='consultation',
        status='Scheduled',
        notes='Fever check'
    )
    db.session.add(appt4)

    # Appt 5: Priya Singh - Dr. Sneha Reddy (Dermatologist) - Today 02:00 PM
    appt5 = Appointment(
        clinic_id=clinic.clinic_id,
        patient_id=patients[3].patient_id,
        doctor_id=doctors[3].doctor_id,
        date=today_str,
        time_slot='02:00 PM',
        type='consultation',
        status='Scheduled',
        notes='Rash consultation'
    )
    db.session.add(appt5)

    # 8. Seed Sync Logs (SMS status logs)
    log1 = SyncLog(
        clinic_id=clinic.clinic_id,
        recipient='+91 98765 43210',
        message_body='Dear Rajesh Verma, your appointment at Apex Care Center with Dr. Rajesh Kumar is scheduled for today at 10:00 AM.',
        status='Sent',
        created_at=datetime.utcnow() - timedelta(hours=5),
        synced_at=datetime.utcnow() - timedelta(hours=4)
    )
    db.session.add(log1)

    log2 = SyncLog(
        clinic_id=clinic.clinic_id,
        recipient='+91 99887 76655',
        message_body='Dear Amit Kumar, your appointment at Apex Care Center with Dr. Priya Sharma is scheduled for today at 11:30 AM.',
        status='Pending', # Offline SMS queue
        created_at=datetime.utcnow() - timedelta(minutes=30)
    )
    db.session.add(log2)

    # 9. Seed Audit Logs
    audit1 = AuditLog(
        clinic_id=clinic.clinic_id,
        action='Clinic Initialization',
        details='Demo clinic seeded with default doctors, patients, inventory, and transaction logs.'
    )
    db.session.add(audit1)

    db.session.commit()
    return clinic
